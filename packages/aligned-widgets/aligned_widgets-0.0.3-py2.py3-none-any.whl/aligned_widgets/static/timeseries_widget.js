// frontend/templates/timeseries_widget.html
var timeseries_widget_default = '<div class="widget timeseries-widget">\n  <div class="header">\n    <span class="title" id="title"></span>\n    <div class="legend" id="legend"></div>\n  </div>\n  <div class="graph" id="canvas-holder">\n    <canvas id="canvas"></canvas>\n  </div>\n  <div class="controls">\n    <div class="left">\n      <div>\n        <button id="btnAdd"></button>\n        <button id="btnDelete"></button>\n      </div>\n      <div class="dropdown">\n        <button class="dropbtn" id="btnToggleTagsList">\n          Edit Tags\n        </button>\n        <div id="tagsList" class="dropdown-content"></div>\n      </div>\n    </div>\n    <div class="right">\n      <button id="btnZoomIn"></button>\n      <button id="btnZoomOut"></button>\n    </div>\n  </div>\n</div>\n';

// frontend/timeseries_widget.ts
var TimeseriesWidget = class {
  constructor({ model, el }) {
    this.tagInputElements = [];
    this.lastAnimationFrameTimestamp = null;
    this.animationFrameRequestId = null;
    this.values = [];
    this.annotations = [];
    this.tags = [];
    this.window_size_in_s = 5;
    this.selectedAnnIndex = null;
    this.selectedResizingHandle = null;
    this.selectedMoveHandle = null;
    this.model = model;
    this.el = el;
    el.innerHTML = timeseries_widget_default;
    this.canvas = el.querySelector("#canvas");
    this.canvas.addEventListener("mousedown", this.canvasMouseDown.bind(this));
    this.canvas.addEventListener("mousemove", this.canvasMouseMove.bind(this));
    this.canvas.addEventListener("mouseup", this.canvasMouseUp.bind(this));
    this.btnAdd = el.querySelector("#btnAdd");
    this.btnAdd.innerHTML = this.model.get("icons").add;
    this.btnAdd.addEventListener("click", this.btnAddClicked.bind(this));
    this.btnDelete = el.querySelector("#btnDelete");
    this.btnDelete.innerHTML = this.model.get("icons").delete;
    this.btnDelete.addEventListener("click", this.btnDeleteClicked.bind(this));
    this.btnZoomIn = el.querySelector("#btnZoomIn");
    this.btnZoomIn.innerHTML = this.model.get("icons").zoom_in;
    this.btnZoomIn.addEventListener("click", this.btnZoomInClicked.bind(this));
    this.btnZoomOut = el.querySelector("#btnZoomOut");
    this.btnZoomOut.innerHTML = this.model.get("icons").zoom_out;
    this.btnZoomOut.addEventListener(
      "click",
      this.btnZoomOutClicked.bind(this)
    );
    this.btnToggleTagsList = el.querySelector("#btnToggleTagsList");
    this.btnToggleTagsList.addEventListener(
      "click",
      this.toggleTagsList.bind(this)
    );
    this.tagsList = el.querySelector("#tagsList");
    this.currentTime = this.model.get("sync_time");
    const times_bytes = this.model.get("times");
    const times_buffer = times_bytes.buffer || times_bytes;
    this.times = new Float64Array(times_buffer);
    const values_bytes = this.model.get("values");
    const values_buffer = values_bytes.buffer || values_bytes;
    const all_values = new Float64Array(values_buffer);
    const num_elements = this.times.length;
    const total_values_count = all_values.length;
    this.numChannels = total_values_count / num_elements;
    for (let i = 0; i < this.numChannels; i++) {
      this.values.push(
        all_values.slice(i * num_elements, i * num_elements + num_elements)
      );
    }
    this.annotations = this.model.get("annotations");
    this.yRange = this.model.get("y_range");
    this.window_size_in_s = this.model.get("x_range");
    this.tags = this.model.get("tags");
    this.populateTagsList();
    this.addLegend();
    this.addTitle();
  }
  populateTagsList() {
    for (let i = 0; i < this.tags.length; i++) {
      const tag = this.tags[i];
      const label = document.createElement("label");
      const inputCheckbox = document.createElement("input");
      const labelText = document.createTextNode(tag);
      inputCheckbox.type = "checkbox";
      inputCheckbox.value = tag;
      inputCheckbox.style.setProperty("--checkbox-color", this.getTagColor(i));
      inputCheckbox.addEventListener("change", this.tagToggled.bind(this));
      label.appendChild(inputCheckbox);
      label.appendChild(labelText);
      this.tagInputElements.push(inputCheckbox);
      this.tagsList.appendChild(label);
    }
  }
  tagToggled(e) {
    if (this.selectedAnnIndex == null) return;
    const target = e.target;
    const ann = this.annotations[this.selectedAnnIndex];
    if (target.checked) {
      ann.tags.push(target.value);
    } else {
      ann.tags = ann.tags.filter((t) => t !== target.value);
    }
    this.syncAnnotations();
  }
  canvasMouseDown(e) {
    if (this.checkForHandleSelection(e.offsetX)) {
      return;
    }
    if (this.checkForAnnSelection(e.offsetX)) {
      this.updateTagCheckboxes();
      this.btnToggleTagsList.classList.add("show");
    } else {
      this.btnToggleTagsList.classList.remove("show");
      this.tagsList.classList.remove("show");
    }
  }
  updateTagCheckboxes() {
    if (this.selectedAnnIndex == null) return;
    const tags = this.annotations[this.selectedAnnIndex].tags;
    for (const checkbox of this.tagInputElements) {
      checkbox.checked = tags.includes(checkbox.value);
    }
  }
  canvasMouseMove(e) {
    if (this.selectedResizingHandle != null) {
      this.resizeAnnotation(e.offsetX);
    } else if (this.selectedMoveHandle != null) {
      this.moveAnnotation(e.offsetX);
    }
  }
  resizeAnnotation(mouseX) {
    if (this.selectedResizingHandle == null) return;
    const width = this.canvas.width;
    const time = this.currentTime + this.window_size_in_s * (mouseX - width / 2) / width;
    if (this.selectedResizingHandle.side == "left") {
      this.annotations[this.selectedResizingHandle.annIndex].start = time;
    } else {
      this.annotations[this.selectedResizingHandle.annIndex].end = time;
    }
  }
  moveAnnotation(mouseX) {
    if (this.selectedMoveHandle == null) return;
    const width = this.canvas.width;
    const offsetTime = this.window_size_in_s * (mouseX - this.selectedMoveHandle.grabX) / width;
    this.annotations[this.selectedMoveHandle.annIndex].start = this.selectedMoveHandle.annStart + offsetTime;
    this.annotations[this.selectedMoveHandle.annIndex].end = this.selectedMoveHandle.annEnd + offsetTime;
  }
  canvasMouseUp() {
    this.selectedResizingHandle = null;
    this.selectedMoveHandle = null;
    this.syncAnnotations();
  }
  btnAddClicked() {
    this.annotations.push({
      start: this.currentTime,
      end: this.currentTime + 0.5,
      tags: []
    });
    this.selectedAnnIndex = this.annotations.length - 1;
    this.syncAnnotations();
  }
  btnDeleteClicked() {
    if (this.selectedAnnIndex == null) return;
    this.annotations.splice(this.selectedAnnIndex, 1);
    this.selectedAnnIndex = null;
    this.syncAnnotations();
  }
  btnZoomInClicked() {
    this.window_size_in_s -= 0.5;
  }
  btnZoomOutClicked() {
    this.window_size_in_s += 0.5;
  }
  toggleTagsList() {
    this.tagsList.classList.toggle("show");
  }
  syncAnnotations() {
    this.model.set("annotations", []);
    this.model.set("annotations", [...this.annotations]);
    this.model.save_changes();
  }
  checkForAnnSelection(mouseX) {
    const startTime = this.currentTime - this.window_size_in_s / 2;
    const endTime = this.currentTime + this.window_size_in_s / 2;
    const drawnAnns = this.getAnnotationsToDraw(startTime, endTime);
    this.selectedAnnIndex = null;
    for (let i = 0; i < drawnAnns.length; i++) {
      const ann = drawnAnns[i];
      if (ann.start > mouseX || ann.start + ann.width < mouseX) continue;
      this.selectedAnnIndex = ann.index;
      return true;
    }
    return false;
  }
  checkForHandleSelection(mouseX) {
    const startTime = this.currentTime - this.window_size_in_s / 2;
    const endTime = this.currentTime + this.window_size_in_s / 2;
    const drawnAnns = this.getAnnotationsToDraw(startTime, endTime);
    this.selectedResizingHandle = null;
    this.selectedMoveHandle = null;
    for (let i = 0; i < drawnAnns.length; i++) {
      const ann = drawnAnns[i];
      if (Math.abs(mouseX - ann.start) < 6) {
        this.selectedResizingHandle = {
          annIndex: ann.index,
          side: "left"
        };
        return true;
      }
      if (Math.abs(mouseX - ann.start - ann.width) < 6) {
        this.selectedResizingHandle = {
          annIndex: ann.index,
          side: "right"
        };
        return true;
      }
      if (mouseX > ann.start && mouseX < ann.start + ann.width) {
        this.selectedMoveHandle = {
          annIndex: ann.index,
          grabX: mouseX,
          annStart: this.annotations[ann.index].start,
          annEnd: this.annotations[ann.index].end
        };
      }
    }
    return false;
  }
  addLegend() {
    const legend = this.el.querySelector("#legend");
    for (const channel of this.model.get("channel_names")) {
      const channelIndex = this.model.get("channel_names").findIndex((e) => e == channel);
      const label = document.createElement("span");
      label.innerHTML = channel;
      label.style.setProperty("--line-color", this.getPlotColor(channelIndex));
      legend.append(label);
    }
  }
  addTitle() {
    const title = this.el.querySelector("#title");
    title.innerHTML = this.model.get("title");
  }
  getPlotColor(channelIndex) {
    const colors = [
      "#F44336",
      "#4CAF50",
      "#2196F3",
      "#FFEB3B",
      "#795548",
      "#673AB7"
    ];
    const index = channelIndex % colors.length;
    return colors[index];
  }
  getTagColor(tagIndex) {
    const colors = [
      "#F44336",
      "#3F51B5",
      "#00BCD4",
      "#9C27B0",
      "#E91E63",
      "#CDDC39",
      "#795548",
      "#FFEB3B",
      "#607D8B",
      "#2196F3"
    ];
    const index = tagIndex % colors.length;
    return colors[index];
  }
  step(timestamp) {
    if (!this.lastAnimationFrameTimestamp) {
      const canvasHolder = this.el.querySelector("#canvas-holder");
      this.canvas.width = canvasHolder.clientWidth;
      this.canvas.height = canvasHolder.clientHeight;
      this.canvas.style.width = "100%";
      this.canvas.style.height = "100%";
      this.lastAnimationFrameTimestamp = timestamp;
    }
    const delta = timestamp - this.lastAnimationFrameTimestamp;
    this.lastAnimationFrameTimestamp = timestamp;
    if (this.model.get("is_running")) {
      const duration = this.times[this.times.length - 1];
      this.currentTime = Math.min(this.currentTime + delta / 1e3, duration);
    }
    this.clearFrame();
    this.draw();
    this.animationFrameRequestId = requestAnimationFrame(this.step);
  }
  draw() {
    const startTime = this.currentTime - this.window_size_in_s / 2;
    const endTime = this.currentTime + this.window_size_in_s / 2;
    const startIndex = this.times.findIndex((e) => e >= startTime);
    const endIndexPlus1 = this.times.findIndex((e) => e > endTime);
    const endIndex = endIndexPlus1 != -1 ? Math.max(endIndexPlus1 - 1, 0) : this.times.length - 1;
    const firstPointTimeDelta = this.times[startIndex] - this.currentTime;
    const lastPointTimeDelta = this.times[endIndex] - this.currentTime;
    const leftOffsetPercentage = Math.max(
      firstPointTimeDelta / this.window_size_in_s + 0.5,
      0
    );
    const rightOffsetPercentage = lastPointTimeDelta / this.window_size_in_s + 0.5;
    this.drawAnnotations(startTime, endTime);
    for (let c = 0; c < this.numChannels; c++) {
      this.drawPlot(
        c,
        startIndex,
        endIndex,
        leftOffsetPercentage,
        rightOffsetPercentage
      );
    }
  }
  getRange(startIndex, endIndex) {
    let min = this.yRange.min;
    let max = this.yRange.max;
    if (min != null && max != null) return { min, max };
    const mins = [];
    const maxs = [];
    for (let c = 0; c < this.numChannels; c++) {
      if (min == null) {
        mins.push(Math.min(...this.values[c].slice(startIndex, endIndex + 1)));
      }
      if (max == null) {
        maxs.push(Math.max(...this.values[c].slice(startIndex, endIndex + 1)));
      }
    }
    return {
      min: min ? min : Math.min(...mins),
      max: max ? max : Math.max(...maxs)
    };
  }
  drawPlot(channelIndex, startIndex, endIndex, leftOffsetPercentage, rightOffsetPercentage) {
    if (isNaN(startIndex) || isNaN(endIndex)) return;
    const ctx = this.canvas.getContext("2d");
    const width = this.canvas.width;
    const height = this.canvas.height;
    if (!ctx) {
      console.error("Failed to get 2D context");
      return;
    }
    ctx.strokeStyle = this.getPlotColor(channelIndex);
    ctx.lineWidth = 2;
    ctx.beginPath();
    const indexRange = endIndex - startIndex;
    const fullWidthRange = width;
    const startX = leftOffsetPercentage * fullWidthRange;
    const endX = rightOffsetPercentage * fullWidthRange;
    const widthRange = endX - startX;
    const heightRange = height;
    const { min, max } = this.getRange(startIndex, endIndex);
    const yRange = max - min;
    const values = this.values[channelIndex];
    ctx.moveTo(
      startX,
      height - heightRange * (values[startIndex] - min) / yRange
    );
    const max_points_to_display = width;
    const di = indexRange > max_points_to_display ? Math.floor(indexRange / max_points_to_display) : 1;
    for (let i = Math.max(0, startIndex - di); i < Math.min(values.length, endIndex + 2 * di); i += di) {
      const x = (i - startIndex) / indexRange * widthRange + startX;
      const y = height - heightRange * (values[i] - min) / yRange;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  getAnnotationsToDraw(startTime, endTime) {
    let annotationsToDraw = [];
    const width = this.canvas.width;
    const leftOffsetPercentage = 0;
    const rightOffsetPercentage = 1;
    const fullWidthRange = width;
    const startX = fullWidthRange * leftOffsetPercentage;
    const endX = fullWidthRange * rightOffsetPercentage;
    const widthRange = endX - startX;
    const timeRange = endTime - startTime;
    for (let i = 0; i < this.annotations.length; i++) {
      const ann = this.annotations[i];
      if (ann.start >= startTime && ann.start <= endTime || ann.end >= startTime && ann.end <= endTime || ann.start <= startTime && ann.end >= endTime) {
        const start = widthRange * (Math.max(ann["start"], startTime) - startTime) / timeRange;
        const end = widthRange * (Math.min(ann["end"], endTime) - startTime) / timeRange;
        annotationsToDraw.push({
          start: startX + start,
          width: end - start,
          tagIndexes: ann.tags.map((t) => this.tags.indexOf(t)),
          index: i
        });
      }
    }
    return annotationsToDraw;
  }
  drawAnnotations(startTime, endTime) {
    const ctx = this.canvas.getContext("2d");
    if (!ctx) {
      console.error("Failed to get 2D context");
      return;
    }
    const height = this.canvas.height;
    const indicatorPadding = 2;
    const indicatorHeight = 5;
    const annotationsToDraw = this.getAnnotationsToDraw(startTime, endTime);
    for (let i = 0; i < annotationsToDraw.length; i++) {
      const ann = annotationsToDraw[i];
      ctx.fillStyle = `#78909C${ann.index == this.selectedAnnIndex ? "44" : "22"}`;
      ctx.fillRect(ann.start, 0, ann.width, height);
      for (let i2 = 0; i2 < ann.tagIndexes.length; i2++) {
        ctx.fillStyle = this.getTagColor(ann.tagIndexes[i2]);
        ctx.fillRect(
          ann.start + indicatorPadding,
          indicatorPadding + i2 * indicatorHeight,
          ann.width - 2 * indicatorPadding,
          indicatorHeight - indicatorPadding
        );
      }
      if (this.selectedAnnIndex == ann.index) {
        ctx.lineCap = "round";
        ctx.strokeStyle = "#78909C";
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(ann.start - 4, height / 2 - 12);
        ctx.lineTo(ann.start - 4, height / 2 + 12);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(ann.start + 4, height / 2 - 12);
        ctx.lineTo(ann.start + 4, height / 2 + 12);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(ann.start + ann.width - 4, height / 2 - 12);
        ctx.lineTo(ann.start + ann.width - 4, height / 2 + 12);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(ann.start + ann.width + 4, height / 2 - 12);
        ctx.lineTo(ann.start + ann.width + 4, height / 2 + 12);
        ctx.stroke();
      }
    }
  }
  clearFrame() {
    const ctx = this.canvas.getContext("2d");
    const width = this.canvas.width;
    const height = this.canvas.height;
    if (!ctx) {
      console.error("Failed to get 2D context");
      return;
    }
    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = "#607d8b";
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(width / 2, 0);
    ctx.lineTo(width / 2, height);
    ctx.stroke();
  }
  syncTimeChanged() {
    this.currentTime = this.model.get("sync_time");
  }
  isRunningChanged() {
  }
  render() {
    this.model.on("change:sync_time", this.syncTimeChanged.bind(this));
    this.model.on("change:is_running", this.isRunningChanged.bind(this));
    this.step = this.step.bind(this);
    this.animationFrameRequestId = requestAnimationFrame(this.step);
  }
  destroy() {
    cancelAnimationFrame(this.animationFrameRequestId);
  }
};
var timeseries_widget_default2 = {
  render(props) {
    const widget = new TimeseriesWidget(props);
    widget.render();
    return () => widget.destroy();
  }
};
export {
  timeseries_widget_default2 as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLi4vLi4vLi4vZnJvbnRlbmQvdGVtcGxhdGVzL3RpbWVzZXJpZXNfd2lkZ2V0Lmh0bWwiLCAiLi4vLi4vLi4vZnJvbnRlbmQvdGltZXNlcmllc193aWRnZXQudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbIjxkaXYgY2xhc3M9XCJ3aWRnZXQgdGltZXNlcmllcy13aWRnZXRcIj5cbiAgPGRpdiBjbGFzcz1cImhlYWRlclwiPlxuICAgIDxzcGFuIGNsYXNzPVwidGl0bGVcIiBpZD1cInRpdGxlXCI+PC9zcGFuPlxuICAgIDxkaXYgY2xhc3M9XCJsZWdlbmRcIiBpZD1cImxlZ2VuZFwiPjwvZGl2PlxuICA8L2Rpdj5cbiAgPGRpdiBjbGFzcz1cImdyYXBoXCIgaWQ9XCJjYW52YXMtaG9sZGVyXCI+XG4gICAgPGNhbnZhcyBpZD1cImNhbnZhc1wiPjwvY2FudmFzPlxuICA8L2Rpdj5cbiAgPGRpdiBjbGFzcz1cImNvbnRyb2xzXCI+XG4gICAgPGRpdiBjbGFzcz1cImxlZnRcIj5cbiAgICAgIDxkaXY+XG4gICAgICAgIDxidXR0b24gaWQ9XCJidG5BZGRcIj48L2J1dHRvbj5cbiAgICAgICAgPGJ1dHRvbiBpZD1cImJ0bkRlbGV0ZVwiPjwvYnV0dG9uPlxuICAgICAgPC9kaXY+XG4gICAgICA8ZGl2IGNsYXNzPVwiZHJvcGRvd25cIj5cbiAgICAgICAgPGJ1dHRvbiBjbGFzcz1cImRyb3BidG5cIiBpZD1cImJ0blRvZ2dsZVRhZ3NMaXN0XCI+XG4gICAgICAgICAgRWRpdCBUYWdzXG4gICAgICAgIDwvYnV0dG9uPlxuICAgICAgICA8ZGl2IGlkPVwidGFnc0xpc3RcIiBjbGFzcz1cImRyb3Bkb3duLWNvbnRlbnRcIj48L2Rpdj5cbiAgICAgIDwvZGl2PlxuICAgIDwvZGl2PlxuICAgIDxkaXYgY2xhc3M9XCJyaWdodFwiPlxuICAgICAgPGJ1dHRvbiBpZD1cImJ0blpvb21JblwiPjwvYnV0dG9uPlxuICAgICAgPGJ1dHRvbiBpZD1cImJ0blpvb21PdXRcIj48L2J1dHRvbj5cbiAgICA8L2Rpdj5cbiAgPC9kaXY+XG48L2Rpdj5cbiIsICJpbXBvcnQgdHlwZSB7IEFueU1vZGVsLCBSZW5kZXJQcm9wcyB9IGZyb20gJ0Bhbnl3aWRnZXQvdHlwZXMnO1xuaW1wb3J0ICcuL3N0eWxlcy93aWRnZXQuY3NzJztcbmltcG9ydCAnLi9zdHlsZXMvdGltZXNlcmllc193aWRnZXQuY3NzJztcbmltcG9ydCB0aW1lc2VyaWVzVGVtcGxhdGUgZnJvbSAnLi90ZW1wbGF0ZXMvdGltZXNlcmllc193aWRnZXQuaHRtbCc7XG5cbnR5cGUgQW5ub3RhdGlvbiA9IHtcbiAgc3RhcnQ6IG51bWJlcjtcbiAgZW5kOiBudW1iZXI7XG4gIHRhZ3M6IHN0cmluZ1tdO1xufTtcblxudHlwZSBZUmFuZ2UgPSB7XG4gIG1pbjogbnVtYmVyIHwgbnVsbDtcbiAgbWF4OiBudW1iZXIgfCBudWxsO1xufTtcblxuaW50ZXJmYWNlIFRpbWVyc2VyaWVzV2lkZ2V0TW9kZWwge1xuICBpc19ydW5uaW5nOiBib29sZWFuO1xuICBzeW5jX3RpbWU6IG51bWJlcjtcbiAgdGltZXM6IEZsb2F0NjRBcnJheTtcbiAgdmFsdWVzOiBGbG9hdDY0QXJyYXk7XG4gIHRhZ3M6IHN0cmluZ1tdO1xuICBhbm5vdGF0aW9uczogQW5ub3RhdGlvbltdO1xuICBjaGFubmVsX25hbWVzOiBzdHJpbmdbXTtcbiAgdGl0bGU6IHN0cmluZztcbiAgeV9yYW5nZTogWVJhbmdlO1xuICB4X3JhbmdlOiBudW1iZXI7XG4gIGljb25zOiB7XG4gICAgYWRkOiBzdHJpbmc7XG4gICAgZGVsZXRlOiBzdHJpbmc7XG4gICAgem9vbV9pbjogc3RyaW5nO1xuICAgIHpvb21fb3V0OiBzdHJpbmc7XG4gIH07XG59XG5cbmNsYXNzIFRpbWVzZXJpZXNXaWRnZXQge1xuICBlbDogSFRNTEVsZW1lbnQ7XG4gIG1vZGVsOiBBbnlNb2RlbDxUaW1lcnNlcmllc1dpZGdldE1vZGVsPjtcblxuICBjYW52YXM6IEhUTUxDYW52YXNFbGVtZW50O1xuICBidG5BZGQ6IEhUTUxCdXR0b25FbGVtZW50O1xuICBidG5EZWxldGU6IEhUTUxCdXR0b25FbGVtZW50O1xuICBidG5ab29tSW46IEhUTUxCdXR0b25FbGVtZW50O1xuICBidG5ab29tT3V0OiBIVE1MQnV0dG9uRWxlbWVudDtcbiAgYnRuVG9nZ2xlVGFnc0xpc3Q6IEhUTUxCdXR0b25FbGVtZW50O1xuICB0YWdzTGlzdDogSFRNTERpdkVsZW1lbnQ7XG4gIHRhZ0lucHV0RWxlbWVudHM6IEhUTUxJbnB1dEVsZW1lbnRbXSA9IFtdO1xuXG4gIGN1cnJlbnRUaW1lOiBudW1iZXI7XG4gIGxhc3RBbmltYXRpb25GcmFtZVRpbWVzdGFtcDogRE9NSGlnaFJlc1RpbWVTdGFtcCB8IG51bGwgPSBudWxsO1xuICBhbmltYXRpb25GcmFtZVJlcXVlc3RJZDogbnVtYmVyIHwgbnVsbCA9IG51bGw7XG5cbiAgdGltZXM6IEZsb2F0NjRBcnJheTtcbiAgdmFsdWVzOiBGbG9hdDY0QXJyYXlbXSA9IFtdO1xuICBudW1DaGFubmVsczogbnVtYmVyO1xuICB5UmFuZ2U6IFlSYW5nZTtcbiAgYW5ub3RhdGlvbnM6IEFubm90YXRpb25bXSA9IFtdO1xuICB0YWdzOiBzdHJpbmdbXSA9IFtdO1xuXG4gIHdpbmRvd19zaXplX2luX3MgPSA1O1xuICBzZWxlY3RlZEFubkluZGV4OiBudW1iZXIgfCBudWxsID0gbnVsbDtcbiAgc2VsZWN0ZWRSZXNpemluZ0hhbmRsZToge1xuICAgIGFubkluZGV4OiBudW1iZXI7XG4gICAgc2lkZTogJ2xlZnQnIHwgJ3JpZ2h0JztcbiAgfSB8IG51bGwgPSBudWxsO1xuICBzZWxlY3RlZE1vdmVIYW5kbGU6IHtcbiAgICBhbm5JbmRleDogbnVtYmVyO1xuICAgIGdyYWJYOiBudW1iZXI7XG4gICAgYW5uU3RhcnQ6IG51bWJlcjtcbiAgICBhbm5FbmQ6IG51bWJlcjtcbiAgfSB8IG51bGwgPSBudWxsO1xuXG4gIGNvbnN0cnVjdG9yKHsgbW9kZWwsIGVsIH06IFJlbmRlclByb3BzPFRpbWVyc2VyaWVzV2lkZ2V0TW9kZWw+KSB7XG4gICAgdGhpcy5tb2RlbCA9IG1vZGVsO1xuICAgIHRoaXMuZWwgPSBlbDtcbiAgICBlbC5pbm5lckhUTUwgPSB0aW1lc2VyaWVzVGVtcGxhdGU7XG5cbiAgICB0aGlzLmNhbnZhcyA9IGVsLnF1ZXJ5U2VsZWN0b3IoJyNjYW52YXMnKSE7XG4gICAgdGhpcy5jYW52YXMuYWRkRXZlbnRMaXN0ZW5lcignbW91c2Vkb3duJywgdGhpcy5jYW52YXNNb3VzZURvd24uYmluZCh0aGlzKSk7XG4gICAgdGhpcy5jYW52YXMuYWRkRXZlbnRMaXN0ZW5lcignbW91c2Vtb3ZlJywgdGhpcy5jYW52YXNNb3VzZU1vdmUuYmluZCh0aGlzKSk7XG4gICAgdGhpcy5jYW52YXMuYWRkRXZlbnRMaXN0ZW5lcignbW91c2V1cCcsIHRoaXMuY2FudmFzTW91c2VVcC5iaW5kKHRoaXMpKTtcblxuICAgIHRoaXMuYnRuQWRkID0gZWwucXVlcnlTZWxlY3RvcignI2J0bkFkZCcpITtcbiAgICB0aGlzLmJ0bkFkZC5pbm5lckhUTUwgPSB0aGlzLm1vZGVsLmdldCgnaWNvbnMnKS5hZGQ7XG4gICAgdGhpcy5idG5BZGQuYWRkRXZlbnRMaXN0ZW5lcignY2xpY2snLCB0aGlzLmJ0bkFkZENsaWNrZWQuYmluZCh0aGlzKSk7XG5cbiAgICB0aGlzLmJ0bkRlbGV0ZSA9IGVsLnF1ZXJ5U2VsZWN0b3IoJyNidG5EZWxldGUnKSE7XG4gICAgdGhpcy5idG5EZWxldGUuaW5uZXJIVE1MID0gdGhpcy5tb2RlbC5nZXQoJ2ljb25zJykuZGVsZXRlO1xuICAgIHRoaXMuYnRuRGVsZXRlLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgdGhpcy5idG5EZWxldGVDbGlja2VkLmJpbmQodGhpcykpO1xuXG4gICAgdGhpcy5idG5ab29tSW4gPSBlbC5xdWVyeVNlbGVjdG9yKCcjYnRuWm9vbUluJykhO1xuICAgIHRoaXMuYnRuWm9vbUluLmlubmVySFRNTCA9IHRoaXMubW9kZWwuZ2V0KCdpY29ucycpLnpvb21faW47XG4gICAgdGhpcy5idG5ab29tSW4uYWRkRXZlbnRMaXN0ZW5lcignY2xpY2snLCB0aGlzLmJ0blpvb21JbkNsaWNrZWQuYmluZCh0aGlzKSk7XG5cbiAgICB0aGlzLmJ0blpvb21PdXQgPSBlbC5xdWVyeVNlbGVjdG9yKCcjYnRuWm9vbU91dCcpITtcbiAgICB0aGlzLmJ0blpvb21PdXQuaW5uZXJIVE1MID0gdGhpcy5tb2RlbC5nZXQoJ2ljb25zJykuem9vbV9vdXQ7XG4gICAgdGhpcy5idG5ab29tT3V0LmFkZEV2ZW50TGlzdGVuZXIoXG4gICAgICAnY2xpY2snLFxuICAgICAgdGhpcy5idG5ab29tT3V0Q2xpY2tlZC5iaW5kKHRoaXMpXG4gICAgKTtcblxuICAgIHRoaXMuYnRuVG9nZ2xlVGFnc0xpc3QgPSBlbC5xdWVyeVNlbGVjdG9yKCcjYnRuVG9nZ2xlVGFnc0xpc3QnKSE7XG4gICAgdGhpcy5idG5Ub2dnbGVUYWdzTGlzdC5hZGRFdmVudExpc3RlbmVyKFxuICAgICAgJ2NsaWNrJyxcbiAgICAgIHRoaXMudG9nZ2xlVGFnc0xpc3QuYmluZCh0aGlzKVxuICAgICk7XG5cbiAgICB0aGlzLnRhZ3NMaXN0ID0gZWwucXVlcnlTZWxlY3RvcignI3RhZ3NMaXN0JykhO1xuXG4gICAgdGhpcy5jdXJyZW50VGltZSA9IHRoaXMubW9kZWwuZ2V0KCdzeW5jX3RpbWUnKTtcblxuICAgIGNvbnN0IHRpbWVzX2J5dGVzID0gdGhpcy5tb2RlbC5nZXQoJ3RpbWVzJyk7XG4gICAgY29uc3QgdGltZXNfYnVmZmVyID0gdGltZXNfYnl0ZXMuYnVmZmVyIHx8IHRpbWVzX2J5dGVzO1xuICAgIHRoaXMudGltZXMgPSBuZXcgRmxvYXQ2NEFycmF5KHRpbWVzX2J1ZmZlcik7XG5cbiAgICBjb25zdCB2YWx1ZXNfYnl0ZXMgPSB0aGlzLm1vZGVsLmdldCgndmFsdWVzJyk7XG4gICAgY29uc3QgdmFsdWVzX2J1ZmZlciA9IHZhbHVlc19ieXRlcy5idWZmZXIgfHwgdmFsdWVzX2J5dGVzO1xuICAgIGNvbnN0IGFsbF92YWx1ZXMgPSBuZXcgRmxvYXQ2NEFycmF5KHZhbHVlc19idWZmZXIpO1xuXG4gICAgY29uc3QgbnVtX2VsZW1lbnRzID0gdGhpcy50aW1lcy5sZW5ndGg7XG4gICAgY29uc3QgdG90YWxfdmFsdWVzX2NvdW50ID0gYWxsX3ZhbHVlcy5sZW5ndGg7XG4gICAgdGhpcy5udW1DaGFubmVscyA9IHRvdGFsX3ZhbHVlc19jb3VudCAvIG51bV9lbGVtZW50cztcblxuICAgIGZvciAobGV0IGkgPSAwOyBpIDwgdGhpcy5udW1DaGFubmVsczsgaSsrKSB7XG4gICAgICB0aGlzLnZhbHVlcy5wdXNoKFxuICAgICAgICBhbGxfdmFsdWVzLnNsaWNlKGkgKiBudW1fZWxlbWVudHMsIGkgKiBudW1fZWxlbWVudHMgKyBudW1fZWxlbWVudHMpXG4gICAgICApO1xuICAgIH1cblxuICAgIHRoaXMuYW5ub3RhdGlvbnMgPSB0aGlzLm1vZGVsLmdldCgnYW5ub3RhdGlvbnMnKTtcbiAgICB0aGlzLnlSYW5nZSA9IHRoaXMubW9kZWwuZ2V0KCd5X3JhbmdlJyk7XG4gICAgdGhpcy53aW5kb3dfc2l6ZV9pbl9zID0gdGhpcy5tb2RlbC5nZXQoJ3hfcmFuZ2UnKTtcbiAgICB0aGlzLnRhZ3MgPSB0aGlzLm1vZGVsLmdldCgndGFncycpO1xuXG4gICAgdGhpcy5wb3B1bGF0ZVRhZ3NMaXN0KCk7XG4gICAgdGhpcy5hZGRMZWdlbmQoKTtcbiAgICB0aGlzLmFkZFRpdGxlKCk7XG4gIH1cblxuICBwb3B1bGF0ZVRhZ3NMaXN0KCkge1xuICAgIGZvciAobGV0IGkgPSAwOyBpIDwgdGhpcy50YWdzLmxlbmd0aDsgaSsrKSB7XG4gICAgICBjb25zdCB0YWcgPSB0aGlzLnRhZ3NbaV07XG5cbiAgICAgIGNvbnN0IGxhYmVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnbGFiZWwnKTtcbiAgICAgIGNvbnN0IGlucHV0Q2hlY2tib3ggPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdpbnB1dCcpO1xuICAgICAgY29uc3QgbGFiZWxUZXh0ID0gZG9jdW1lbnQuY3JlYXRlVGV4dE5vZGUodGFnKTtcblxuICAgICAgaW5wdXRDaGVja2JveC50eXBlID0gJ2NoZWNrYm94JztcbiAgICAgIGlucHV0Q2hlY2tib3gudmFsdWUgPSB0YWc7XG4gICAgICBpbnB1dENoZWNrYm94LnN0eWxlLnNldFByb3BlcnR5KCctLWNoZWNrYm94LWNvbG9yJywgdGhpcy5nZXRUYWdDb2xvcihpKSk7XG4gICAgICBpbnB1dENoZWNrYm94LmFkZEV2ZW50TGlzdGVuZXIoJ2NoYW5nZScsIHRoaXMudGFnVG9nZ2xlZC5iaW5kKHRoaXMpKTtcblxuICAgICAgbGFiZWwuYXBwZW5kQ2hpbGQoaW5wdXRDaGVja2JveCk7XG4gICAgICBsYWJlbC5hcHBlbmRDaGlsZChsYWJlbFRleHQpO1xuXG4gICAgICB0aGlzLnRhZ0lucHV0RWxlbWVudHMucHVzaChpbnB1dENoZWNrYm94KTtcbiAgICAgIHRoaXMudGFnc0xpc3QuYXBwZW5kQ2hpbGQobGFiZWwpO1xuICAgIH1cbiAgfVxuXG4gIHRhZ1RvZ2dsZWQoZTogRXZlbnQpIHtcbiAgICBpZiAodGhpcy5zZWxlY3RlZEFubkluZGV4ID09IG51bGwpIHJldHVybjtcblxuICAgIGNvbnN0IHRhcmdldCA9IGUudGFyZ2V0IGFzIEhUTUxJbnB1dEVsZW1lbnQ7XG4gICAgY29uc3QgYW5uID0gdGhpcy5hbm5vdGF0aW9uc1t0aGlzLnNlbGVjdGVkQW5uSW5kZXhdO1xuXG4gICAgaWYgKHRhcmdldC5jaGVja2VkKSB7XG4gICAgICBhbm4udGFncy5wdXNoKHRhcmdldC52YWx1ZSk7XG4gICAgfSBlbHNlIHtcbiAgICAgIGFubi50YWdzID0gYW5uLnRhZ3MuZmlsdGVyKHQgPT4gdCAhPT0gdGFyZ2V0LnZhbHVlKTtcbiAgICB9XG5cbiAgICB0aGlzLnN5bmNBbm5vdGF0aW9ucygpO1xuICB9XG5cbiAgY2FudmFzTW91c2VEb3duKGU6IE1vdXNlRXZlbnQpIHtcbiAgICBpZiAodGhpcy5jaGVja0ZvckhhbmRsZVNlbGVjdGlvbihlLm9mZnNldFgpKSB7XG4gICAgICByZXR1cm47XG4gICAgfVxuXG4gICAgaWYgKHRoaXMuY2hlY2tGb3JBbm5TZWxlY3Rpb24oZS5vZmZzZXRYKSkge1xuICAgICAgdGhpcy51cGRhdGVUYWdDaGVja2JveGVzKCk7XG4gICAgICB0aGlzLmJ0blRvZ2dsZVRhZ3NMaXN0LmNsYXNzTGlzdC5hZGQoJ3Nob3cnKTtcbiAgICB9IGVsc2Uge1xuICAgICAgdGhpcy5idG5Ub2dnbGVUYWdzTGlzdC5jbGFzc0xpc3QucmVtb3ZlKCdzaG93Jyk7XG4gICAgICB0aGlzLnRhZ3NMaXN0LmNsYXNzTGlzdC5yZW1vdmUoJ3Nob3cnKTtcbiAgICB9XG4gIH1cblxuICB1cGRhdGVUYWdDaGVja2JveGVzKCkge1xuICAgIGlmICh0aGlzLnNlbGVjdGVkQW5uSW5kZXggPT0gbnVsbCkgcmV0dXJuO1xuICAgIGNvbnN0IHRhZ3MgPSB0aGlzLmFubm90YXRpb25zW3RoaXMuc2VsZWN0ZWRBbm5JbmRleF0udGFncztcblxuICAgIGZvciAoY29uc3QgY2hlY2tib3ggb2YgdGhpcy50YWdJbnB1dEVsZW1lbnRzKSB7XG4gICAgICBjaGVja2JveC5jaGVja2VkID0gdGFncy5pbmNsdWRlcyhjaGVja2JveC52YWx1ZSk7XG4gICAgfVxuICB9XG5cbiAgY2FudmFzTW91c2VNb3ZlKGU6IE1vdXNlRXZlbnQpIHtcbiAgICBpZiAodGhpcy5zZWxlY3RlZFJlc2l6aW5nSGFuZGxlICE9IG51bGwpIHtcbiAgICAgIHRoaXMucmVzaXplQW5ub3RhdGlvbihlLm9mZnNldFgpO1xuICAgIH0gZWxzZSBpZiAodGhpcy5zZWxlY3RlZE1vdmVIYW5kbGUgIT0gbnVsbCkge1xuICAgICAgdGhpcy5tb3ZlQW5ub3RhdGlvbihlLm9mZnNldFgpO1xuICAgIH1cbiAgfVxuXG4gIHJlc2l6ZUFubm90YXRpb24obW91c2VYOiBudW1iZXIpIHtcbiAgICBpZiAodGhpcy5zZWxlY3RlZFJlc2l6aW5nSGFuZGxlID09IG51bGwpIHJldHVybjtcblxuICAgIGNvbnN0IHdpZHRoID0gdGhpcy5jYW52YXMud2lkdGg7XG4gICAgY29uc3QgdGltZSA9XG4gICAgICB0aGlzLmN1cnJlbnRUaW1lICsgKHRoaXMud2luZG93X3NpemVfaW5fcyAqIChtb3VzZVggLSB3aWR0aCAvIDIpKSAvIHdpZHRoO1xuXG4gICAgaWYgKHRoaXMuc2VsZWN0ZWRSZXNpemluZ0hhbmRsZS5zaWRlID09ICdsZWZ0Jykge1xuICAgICAgdGhpcy5hbm5vdGF0aW9uc1t0aGlzLnNlbGVjdGVkUmVzaXppbmdIYW5kbGUuYW5uSW5kZXhdLnN0YXJ0ID0gdGltZTtcbiAgICB9IGVsc2Uge1xuICAgICAgdGhpcy5hbm5vdGF0aW9uc1t0aGlzLnNlbGVjdGVkUmVzaXppbmdIYW5kbGUuYW5uSW5kZXhdLmVuZCA9IHRpbWU7XG4gICAgfVxuICB9XG5cbiAgbW92ZUFubm90YXRpb24obW91c2VYOiBudW1iZXIpIHtcbiAgICBpZiAodGhpcy5zZWxlY3RlZE1vdmVIYW5kbGUgPT0gbnVsbCkgcmV0dXJuO1xuXG4gICAgY29uc3Qgd2lkdGggPSB0aGlzLmNhbnZhcy53aWR0aDtcbiAgICBjb25zdCBvZmZzZXRUaW1lID1cbiAgICAgICh0aGlzLndpbmRvd19zaXplX2luX3MgKiAobW91c2VYIC0gdGhpcy5zZWxlY3RlZE1vdmVIYW5kbGUuZ3JhYlgpKSAvXG4gICAgICB3aWR0aDtcbiAgICB0aGlzLmFubm90YXRpb25zW3RoaXMuc2VsZWN0ZWRNb3ZlSGFuZGxlLmFubkluZGV4XS5zdGFydCA9XG4gICAgICB0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZS5hbm5TdGFydCArIG9mZnNldFRpbWU7XG4gICAgdGhpcy5hbm5vdGF0aW9uc1t0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZS5hbm5JbmRleF0uZW5kID1cbiAgICAgIHRoaXMuc2VsZWN0ZWRNb3ZlSGFuZGxlLmFubkVuZCArIG9mZnNldFRpbWU7XG4gIH1cblxuICBjYW52YXNNb3VzZVVwKCkge1xuICAgIHRoaXMuc2VsZWN0ZWRSZXNpemluZ0hhbmRsZSA9IG51bGw7XG4gICAgdGhpcy5zZWxlY3RlZE1vdmVIYW5kbGUgPSBudWxsO1xuICAgIHRoaXMuc3luY0Fubm90YXRpb25zKCk7XG4gIH1cblxuICBidG5BZGRDbGlja2VkKCkge1xuICAgIHRoaXMuYW5ub3RhdGlvbnMucHVzaCh7XG4gICAgICBzdGFydDogdGhpcy5jdXJyZW50VGltZSxcbiAgICAgIGVuZDogdGhpcy5jdXJyZW50VGltZSArIDAuNSxcbiAgICAgIHRhZ3M6IFtdLFxuICAgIH0pO1xuXG4gICAgdGhpcy5zZWxlY3RlZEFubkluZGV4ID0gdGhpcy5hbm5vdGF0aW9ucy5sZW5ndGggLSAxO1xuXG4gICAgdGhpcy5zeW5jQW5ub3RhdGlvbnMoKTtcbiAgfVxuXG4gIGJ0bkRlbGV0ZUNsaWNrZWQoKSB7XG4gICAgaWYgKHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA9PSBudWxsKSByZXR1cm47XG5cbiAgICB0aGlzLmFubm90YXRpb25zLnNwbGljZSh0aGlzLnNlbGVjdGVkQW5uSW5kZXgsIDEpO1xuICAgIHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA9IG51bGw7XG5cbiAgICB0aGlzLnN5bmNBbm5vdGF0aW9ucygpO1xuICB9XG5cbiAgYnRuWm9vbUluQ2xpY2tlZCgpIHtcbiAgICB0aGlzLndpbmRvd19zaXplX2luX3MgLT0gMC41O1xuICB9XG5cbiAgYnRuWm9vbU91dENsaWNrZWQoKSB7XG4gICAgdGhpcy53aW5kb3dfc2l6ZV9pbl9zICs9IDAuNTtcbiAgfVxuXG4gIHRvZ2dsZVRhZ3NMaXN0KCkge1xuICAgIHRoaXMudGFnc0xpc3QuY2xhc3NMaXN0LnRvZ2dsZSgnc2hvdycpO1xuICB9XG5cbiAgc3luY0Fubm90YXRpb25zKCkge1xuICAgIHRoaXMubW9kZWwuc2V0KCdhbm5vdGF0aW9ucycsIFtdKTtcbiAgICB0aGlzLm1vZGVsLnNldCgnYW5ub3RhdGlvbnMnLCBbLi4udGhpcy5hbm5vdGF0aW9uc10pO1xuICAgIHRoaXMubW9kZWwuc2F2ZV9jaGFuZ2VzKCk7XG4gIH1cblxuICBjaGVja0ZvckFublNlbGVjdGlvbihtb3VzZVg6IG51bWJlcikge1xuICAgIGNvbnN0IHN0YXJ0VGltZSA9IHRoaXMuY3VycmVudFRpbWUgLSB0aGlzLndpbmRvd19zaXplX2luX3MgLyAyO1xuICAgIGNvbnN0IGVuZFRpbWUgPSB0aGlzLmN1cnJlbnRUaW1lICsgdGhpcy53aW5kb3dfc2l6ZV9pbl9zIC8gMjtcblxuICAgIGNvbnN0IGRyYXduQW5ucyA9IHRoaXMuZ2V0QW5ub3RhdGlvbnNUb0RyYXcoc3RhcnRUaW1lLCBlbmRUaW1lKTtcblxuICAgIHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA9IG51bGw7XG4gICAgZm9yIChsZXQgaSA9IDA7IGkgPCBkcmF3bkFubnMubGVuZ3RoOyBpKyspIHtcbiAgICAgIGNvbnN0IGFubiA9IGRyYXduQW5uc1tpXTtcbiAgICAgIGlmIChhbm4uc3RhcnQgPiBtb3VzZVggfHwgYW5uLnN0YXJ0ICsgYW5uLndpZHRoIDwgbW91c2VYKSBjb250aW51ZTtcbiAgICAgIHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA9IGFubi5pbmRleDtcbiAgICAgIHJldHVybiB0cnVlO1xuICAgIH1cblxuICAgIHJldHVybiBmYWxzZTtcbiAgfVxuXG4gIGNoZWNrRm9ySGFuZGxlU2VsZWN0aW9uKG1vdXNlWDogbnVtYmVyKSB7XG4gICAgY29uc3Qgc3RhcnRUaW1lID0gdGhpcy5jdXJyZW50VGltZSAtIHRoaXMud2luZG93X3NpemVfaW5fcyAvIDI7XG4gICAgY29uc3QgZW5kVGltZSA9IHRoaXMuY3VycmVudFRpbWUgKyB0aGlzLndpbmRvd19zaXplX2luX3MgLyAyO1xuXG4gICAgY29uc3QgZHJhd25Bbm5zID0gdGhpcy5nZXRBbm5vdGF0aW9uc1RvRHJhdyhzdGFydFRpbWUsIGVuZFRpbWUpO1xuXG4gICAgdGhpcy5zZWxlY3RlZFJlc2l6aW5nSGFuZGxlID0gbnVsbDtcbiAgICB0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZSA9IG51bGw7XG4gICAgZm9yIChsZXQgaSA9IDA7IGkgPCBkcmF3bkFubnMubGVuZ3RoOyBpKyspIHtcbiAgICAgIGNvbnN0IGFubiA9IGRyYXduQW5uc1tpXTtcblxuICAgICAgLy8gQ2hlY2sgZm9yIGxlZnQgaGFuZGxlXG4gICAgICBpZiAoTWF0aC5hYnMobW91c2VYIC0gYW5uLnN0YXJ0KSA8IDYpIHtcbiAgICAgICAgdGhpcy5zZWxlY3RlZFJlc2l6aW5nSGFuZGxlID0ge1xuICAgICAgICAgIGFubkluZGV4OiBhbm4uaW5kZXgsXG4gICAgICAgICAgc2lkZTogJ2xlZnQnLFxuICAgICAgICB9O1xuICAgICAgICByZXR1cm4gdHJ1ZTtcbiAgICAgIH1cblxuICAgICAgLy8gQ2hlY2sgZm9yIHJpZ2h0IGhhbmRsZVxuICAgICAgaWYgKE1hdGguYWJzKG1vdXNlWCAtIGFubi5zdGFydCAtIGFubi53aWR0aCkgPCA2KSB7XG4gICAgICAgIHRoaXMuc2VsZWN0ZWRSZXNpemluZ0hhbmRsZSA9IHtcbiAgICAgICAgICBhbm5JbmRleDogYW5uLmluZGV4LFxuICAgICAgICAgIHNpZGU6ICdyaWdodCcsXG4gICAgICAgIH07XG4gICAgICAgIHJldHVybiB0cnVlO1xuICAgICAgfVxuXG4gICAgICAvLyBNb3ZlIGhhbmRsZVxuICAgICAgaWYgKG1vdXNlWCA+IGFubi5zdGFydCAmJiBtb3VzZVggPCBhbm4uc3RhcnQgKyBhbm4ud2lkdGgpIHtcbiAgICAgICAgdGhpcy5zZWxlY3RlZE1vdmVIYW5kbGUgPSB7XG4gICAgICAgICAgYW5uSW5kZXg6IGFubi5pbmRleCxcbiAgICAgICAgICBncmFiWDogbW91c2VYLFxuICAgICAgICAgIGFublN0YXJ0OiB0aGlzLmFubm90YXRpb25zW2Fubi5pbmRleF0uc3RhcnQsXG4gICAgICAgICAgYW5uRW5kOiB0aGlzLmFubm90YXRpb25zW2Fubi5pbmRleF0uZW5kLFxuICAgICAgICB9O1xuICAgICAgfVxuICAgIH1cblxuICAgIHJldHVybiBmYWxzZTtcbiAgfVxuXG4gIGFkZExlZ2VuZCgpIHtcbiAgICBjb25zdCBsZWdlbmQgPSB0aGlzLmVsLnF1ZXJ5U2VsZWN0b3IoJyNsZWdlbmQnKSE7XG5cbiAgICBmb3IgKGNvbnN0IGNoYW5uZWwgb2YgdGhpcy5tb2RlbC5nZXQoJ2NoYW5uZWxfbmFtZXMnKSkge1xuICAgICAgY29uc3QgY2hhbm5lbEluZGV4ID0gdGhpcy5tb2RlbFxuICAgICAgICAuZ2V0KCdjaGFubmVsX25hbWVzJylcbiAgICAgICAgLmZpbmRJbmRleChlID0+IGUgPT0gY2hhbm5lbCk7XG4gICAgICBjb25zdCBsYWJlbCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ3NwYW4nKTtcbiAgICAgIGxhYmVsLmlubmVySFRNTCA9IGNoYW5uZWw7XG4gICAgICBsYWJlbC5zdHlsZS5zZXRQcm9wZXJ0eSgnLS1saW5lLWNvbG9yJywgdGhpcy5nZXRQbG90Q29sb3IoY2hhbm5lbEluZGV4KSk7XG4gICAgICBsZWdlbmQuYXBwZW5kKGxhYmVsKTtcbiAgICB9XG4gIH1cblxuICBhZGRUaXRsZSgpIHtcbiAgICBjb25zdCB0aXRsZSA9IHRoaXMuZWwucXVlcnlTZWxlY3RvcignI3RpdGxlJykhO1xuICAgIHRpdGxlLmlubmVySFRNTCA9IHRoaXMubW9kZWwuZ2V0KCd0aXRsZScpO1xuICB9XG5cbiAgZ2V0UGxvdENvbG9yKGNoYW5uZWxJbmRleDogbnVtYmVyKSB7XG4gICAgY29uc3QgY29sb3JzID0gW1xuICAgICAgJyNGNDQzMzYnLFxuICAgICAgJyM0Q0FGNTAnLFxuICAgICAgJyMyMTk2RjMnLFxuICAgICAgJyNGRkVCM0InLFxuICAgICAgJyM3OTU1NDgnLFxuICAgICAgJyM2NzNBQjcnLFxuICAgIF07XG5cbiAgICBjb25zdCBpbmRleCA9IGNoYW5uZWxJbmRleCAlIGNvbG9ycy5sZW5ndGg7XG5cbiAgICByZXR1cm4gY29sb3JzW2luZGV4XTtcbiAgfVxuXG4gIGdldFRhZ0NvbG9yKHRhZ0luZGV4OiBudW1iZXIpIHtcbiAgICBjb25zdCBjb2xvcnMgPSBbXG4gICAgICAnI0Y0NDMzNicsXG4gICAgICAnIzNGNTFCNScsXG4gICAgICAnIzAwQkNENCcsXG4gICAgICAnIzlDMjdCMCcsXG4gICAgICAnI0U5MUU2MycsXG4gICAgICAnI0NEREMzOScsXG4gICAgICAnIzc5NTU0OCcsXG4gICAgICAnI0ZGRUIzQicsXG4gICAgICAnIzYwN0Q4QicsXG4gICAgICAnIzIxOTZGMycsXG4gICAgXTtcblxuICAgIGNvbnN0IGluZGV4ID0gdGFnSW5kZXggJSBjb2xvcnMubGVuZ3RoO1xuXG4gICAgcmV0dXJuIGNvbG9yc1tpbmRleF07XG4gIH1cblxuICBzdGVwKHRpbWVzdGFtcDogRE9NSGlnaFJlc1RpbWVTdGFtcCkge1xuICAgIGlmICghdGhpcy5sYXN0QW5pbWF0aW9uRnJhbWVUaW1lc3RhbXApIHtcbiAgICAgIGNvbnN0IGNhbnZhc0hvbGRlciA9IHRoaXMuZWwucXVlcnlTZWxlY3RvcignI2NhbnZhcy1ob2xkZXInKSE7XG4gICAgICB0aGlzLmNhbnZhcy53aWR0aCA9IGNhbnZhc0hvbGRlci5jbGllbnRXaWR0aDtcbiAgICAgIHRoaXMuY2FudmFzLmhlaWdodCA9IGNhbnZhc0hvbGRlci5jbGllbnRIZWlnaHQ7XG4gICAgICB0aGlzLmNhbnZhcy5zdHlsZS53aWR0aCA9ICcxMDAlJztcbiAgICAgIHRoaXMuY2FudmFzLnN0eWxlLmhlaWdodCA9ICcxMDAlJztcblxuICAgICAgdGhpcy5sYXN0QW5pbWF0aW9uRnJhbWVUaW1lc3RhbXAgPSB0aW1lc3RhbXA7XG4gICAgfVxuXG4gICAgY29uc3QgZGVsdGEgPSB0aW1lc3RhbXAgLSB0aGlzLmxhc3RBbmltYXRpb25GcmFtZVRpbWVzdGFtcDtcbiAgICB0aGlzLmxhc3RBbmltYXRpb25GcmFtZVRpbWVzdGFtcCA9IHRpbWVzdGFtcDtcblxuICAgIGlmICh0aGlzLm1vZGVsLmdldCgnaXNfcnVubmluZycpKSB7XG4gICAgICBjb25zdCBkdXJhdGlvbiA9IHRoaXMudGltZXNbdGhpcy50aW1lcy5sZW5ndGggLSAxXTtcbiAgICAgIHRoaXMuY3VycmVudFRpbWUgPSBNYXRoLm1pbih0aGlzLmN1cnJlbnRUaW1lICsgZGVsdGEgLyAxMDAwLCBkdXJhdGlvbik7XG4gICAgfVxuXG4gICAgdGhpcy5jbGVhckZyYW1lKCk7XG4gICAgdGhpcy5kcmF3KCk7XG5cbiAgICB0aGlzLmFuaW1hdGlvbkZyYW1lUmVxdWVzdElkID0gcmVxdWVzdEFuaW1hdGlvbkZyYW1lKHRoaXMuc3RlcCk7XG4gIH1cblxuICBkcmF3KCkge1xuICAgIGNvbnN0IHN0YXJ0VGltZSA9IHRoaXMuY3VycmVudFRpbWUgLSB0aGlzLndpbmRvd19zaXplX2luX3MgLyAyO1xuICAgIGNvbnN0IGVuZFRpbWUgPSB0aGlzLmN1cnJlbnRUaW1lICsgdGhpcy53aW5kb3dfc2l6ZV9pbl9zIC8gMjtcblxuICAgIGNvbnN0IHN0YXJ0SW5kZXggPSB0aGlzLnRpbWVzLmZpbmRJbmRleChlID0+IGUgPj0gc3RhcnRUaW1lKTtcbiAgICBjb25zdCBlbmRJbmRleFBsdXMxID0gdGhpcy50aW1lcy5maW5kSW5kZXgoZSA9PiBlID4gZW5kVGltZSk7XG5cbiAgICBjb25zdCBlbmRJbmRleCA9XG4gICAgICBlbmRJbmRleFBsdXMxICE9IC0xXG4gICAgICAgID8gTWF0aC5tYXgoZW5kSW5kZXhQbHVzMSAtIDEsIDApXG4gICAgICAgIDogdGhpcy50aW1lcy5sZW5ndGggLSAxO1xuXG4gICAgY29uc3QgZmlyc3RQb2ludFRpbWVEZWx0YSA9IHRoaXMudGltZXNbc3RhcnRJbmRleF0gLSB0aGlzLmN1cnJlbnRUaW1lO1xuICAgIGNvbnN0IGxhc3RQb2ludFRpbWVEZWx0YSA9IHRoaXMudGltZXNbZW5kSW5kZXhdIC0gdGhpcy5jdXJyZW50VGltZTtcbiAgICBjb25zdCBsZWZ0T2Zmc2V0UGVyY2VudGFnZSA9IE1hdGgubWF4KFxuICAgICAgZmlyc3RQb2ludFRpbWVEZWx0YSAvIHRoaXMud2luZG93X3NpemVfaW5fcyArIDAuNSxcbiAgICAgIDBcbiAgICApO1xuICAgIGNvbnN0IHJpZ2h0T2Zmc2V0UGVyY2VudGFnZSA9XG4gICAgICBsYXN0UG9pbnRUaW1lRGVsdGEgLyB0aGlzLndpbmRvd19zaXplX2luX3MgKyAwLjU7XG5cbiAgICB0aGlzLmRyYXdBbm5vdGF0aW9ucyhzdGFydFRpbWUsIGVuZFRpbWUpO1xuXG4gICAgZm9yIChsZXQgYyA9IDA7IGMgPCB0aGlzLm51bUNoYW5uZWxzOyBjKyspIHtcbiAgICAgIHRoaXMuZHJhd1Bsb3QoXG4gICAgICAgIGMsXG4gICAgICAgIHN0YXJ0SW5kZXgsXG4gICAgICAgIGVuZEluZGV4LFxuICAgICAgICBsZWZ0T2Zmc2V0UGVyY2VudGFnZSxcbiAgICAgICAgcmlnaHRPZmZzZXRQZXJjZW50YWdlXG4gICAgICApO1xuICAgIH1cbiAgfVxuXG4gIGdldFJhbmdlKHN0YXJ0SW5kZXg6IG51bWJlciwgZW5kSW5kZXg6IG51bWJlcikge1xuICAgIGxldCBtaW4gPSB0aGlzLnlSYW5nZS5taW47XG4gICAgbGV0IG1heCA9IHRoaXMueVJhbmdlLm1heDtcblxuICAgIGlmIChtaW4gIT0gbnVsbCAmJiBtYXggIT0gbnVsbCkgcmV0dXJuIHsgbWluLCBtYXggfTtcblxuICAgIGNvbnN0IG1pbnMgPSBbXTtcbiAgICBjb25zdCBtYXhzID0gW107XG5cbiAgICBmb3IgKGxldCBjID0gMDsgYyA8IHRoaXMubnVtQ2hhbm5lbHM7IGMrKykge1xuICAgICAgaWYgKG1pbiA9PSBudWxsKSB7XG4gICAgICAgIG1pbnMucHVzaChNYXRoLm1pbiguLi50aGlzLnZhbHVlc1tjXS5zbGljZShzdGFydEluZGV4LCBlbmRJbmRleCArIDEpKSk7XG4gICAgICB9XG4gICAgICBpZiAobWF4ID09IG51bGwpIHtcbiAgICAgICAgbWF4cy5wdXNoKE1hdGgubWF4KC4uLnRoaXMudmFsdWVzW2NdLnNsaWNlKHN0YXJ0SW5kZXgsIGVuZEluZGV4ICsgMSkpKTtcbiAgICAgIH1cbiAgICB9XG5cbiAgICByZXR1cm4ge1xuICAgICAgbWluOiBtaW4gPyBtaW4gOiBNYXRoLm1pbiguLi5taW5zKSxcbiAgICAgIG1heDogbWF4ID8gbWF4IDogTWF0aC5tYXgoLi4ubWF4cyksXG4gICAgfTtcbiAgfVxuXG4gIGRyYXdQbG90KFxuICAgIGNoYW5uZWxJbmRleDogbnVtYmVyLFxuICAgIHN0YXJ0SW5kZXg6IG51bWJlcixcbiAgICBlbmRJbmRleDogbnVtYmVyLFxuICAgIGxlZnRPZmZzZXRQZXJjZW50YWdlOiBudW1iZXIsXG4gICAgcmlnaHRPZmZzZXRQZXJjZW50YWdlOiBudW1iZXJcbiAgKSB7XG4gICAgaWYgKGlzTmFOKHN0YXJ0SW5kZXgpIHx8IGlzTmFOKGVuZEluZGV4KSkgcmV0dXJuO1xuXG4gICAgY29uc3QgY3R4ID0gdGhpcy5jYW52YXMuZ2V0Q29udGV4dCgnMmQnKTtcbiAgICBjb25zdCB3aWR0aCA9IHRoaXMuY2FudmFzLndpZHRoO1xuICAgIGNvbnN0IGhlaWdodCA9IHRoaXMuY2FudmFzLmhlaWdodDtcblxuICAgIGlmICghY3R4KSB7XG4gICAgICBjb25zb2xlLmVycm9yKCdGYWlsZWQgdG8gZ2V0IDJEIGNvbnRleHQnKTtcbiAgICAgIHJldHVybjtcbiAgICB9XG5cbiAgICBjdHguc3Ryb2tlU3R5bGUgPSB0aGlzLmdldFBsb3RDb2xvcihjaGFubmVsSW5kZXgpO1xuICAgIGN0eC5saW5lV2lkdGggPSAyO1xuXG4gICAgY3R4LmJlZ2luUGF0aCgpO1xuXG4gICAgY29uc3QgaW5kZXhSYW5nZSA9IGVuZEluZGV4IC0gc3RhcnRJbmRleDtcbiAgICBjb25zdCBmdWxsV2lkdGhSYW5nZSA9IHdpZHRoO1xuICAgIGNvbnN0IHN0YXJ0WCA9IGxlZnRPZmZzZXRQZXJjZW50YWdlICogZnVsbFdpZHRoUmFuZ2U7XG4gICAgY29uc3QgZW5kWCA9IHJpZ2h0T2Zmc2V0UGVyY2VudGFnZSAqIGZ1bGxXaWR0aFJhbmdlO1xuICAgIGNvbnN0IHdpZHRoUmFuZ2UgPSBlbmRYIC0gc3RhcnRYO1xuICAgIGNvbnN0IGhlaWdodFJhbmdlID0gaGVpZ2h0O1xuICAgIGNvbnN0IHsgbWluLCBtYXggfSA9IHRoaXMuZ2V0UmFuZ2Uoc3RhcnRJbmRleCwgZW5kSW5kZXgpO1xuICAgIGNvbnN0IHlSYW5nZSA9IG1heCAtIG1pbjtcblxuICAgIGNvbnN0IHZhbHVlcyA9IHRoaXMudmFsdWVzW2NoYW5uZWxJbmRleF07XG5cbiAgICBjdHgubW92ZVRvKFxuICAgICAgc3RhcnRYLFxuICAgICAgaGVpZ2h0IC0gKGhlaWdodFJhbmdlICogKHZhbHVlc1tzdGFydEluZGV4XSAtIG1pbikpIC8geVJhbmdlXG4gICAgKTtcblxuICAgIGNvbnN0IG1heF9wb2ludHNfdG9fZGlzcGxheSA9IHdpZHRoO1xuICAgIGNvbnN0IGRpID1cbiAgICAgIGluZGV4UmFuZ2UgPiBtYXhfcG9pbnRzX3RvX2Rpc3BsYXlcbiAgICAgICAgPyBNYXRoLmZsb29yKGluZGV4UmFuZ2UgLyBtYXhfcG9pbnRzX3RvX2Rpc3BsYXkpXG4gICAgICAgIDogMTtcblxuICAgIGZvciAoXG4gICAgICBsZXQgaSA9IE1hdGgubWF4KDAsIHN0YXJ0SW5kZXggLSBkaSk7XG4gICAgICBpIDwgTWF0aC5taW4odmFsdWVzLmxlbmd0aCwgZW5kSW5kZXggKyAyICogZGkpO1xuICAgICAgaSArPSBkaVxuICAgICkge1xuICAgICAgY29uc3QgeCA9ICgoaSAtIHN0YXJ0SW5kZXgpIC8gaW5kZXhSYW5nZSkgKiB3aWR0aFJhbmdlICsgc3RhcnRYO1xuICAgICAgY29uc3QgeSA9IGhlaWdodCAtIChoZWlnaHRSYW5nZSAqICh2YWx1ZXNbaV0gLSBtaW4pKSAvIHlSYW5nZTtcbiAgICAgIGN0eC5saW5lVG8oeCwgeSk7XG4gICAgfVxuXG4gICAgY3R4LnN0cm9rZSgpO1xuICB9XG5cbiAgZ2V0QW5ub3RhdGlvbnNUb0RyYXcoc3RhcnRUaW1lOiBudW1iZXIsIGVuZFRpbWU6IG51bWJlcikge1xuICAgIGxldCBhbm5vdGF0aW9uc1RvRHJhdyA9IFtdO1xuXG4gICAgY29uc3Qgd2lkdGggPSB0aGlzLmNhbnZhcy53aWR0aDtcblxuICAgIGNvbnN0IGxlZnRPZmZzZXRQZXJjZW50YWdlID0gMDtcbiAgICBjb25zdCByaWdodE9mZnNldFBlcmNlbnRhZ2UgPSAxO1xuXG4gICAgY29uc3QgZnVsbFdpZHRoUmFuZ2UgPSB3aWR0aDtcbiAgICBjb25zdCBzdGFydFggPSBmdWxsV2lkdGhSYW5nZSAqIGxlZnRPZmZzZXRQZXJjZW50YWdlO1xuICAgIGNvbnN0IGVuZFggPSBmdWxsV2lkdGhSYW5nZSAqIHJpZ2h0T2Zmc2V0UGVyY2VudGFnZTtcbiAgICBjb25zdCB3aWR0aFJhbmdlID0gZW5kWCAtIHN0YXJ0WDtcbiAgICBjb25zdCB0aW1lUmFuZ2UgPSBlbmRUaW1lIC0gc3RhcnRUaW1lO1xuXG4gICAgZm9yIChsZXQgaSA9IDA7IGkgPCB0aGlzLmFubm90YXRpb25zLmxlbmd0aDsgaSsrKSB7XG4gICAgICBjb25zdCBhbm4gPSB0aGlzLmFubm90YXRpb25zW2ldO1xuICAgICAgaWYgKFxuICAgICAgICAoYW5uLnN0YXJ0ID49IHN0YXJ0VGltZSAmJiBhbm4uc3RhcnQgPD0gZW5kVGltZSkgfHxcbiAgICAgICAgKGFubi5lbmQgPj0gc3RhcnRUaW1lICYmIGFubi5lbmQgPD0gZW5kVGltZSkgfHxcbiAgICAgICAgKGFubi5zdGFydCA8PSBzdGFydFRpbWUgJiYgYW5uLmVuZCA+PSBlbmRUaW1lKVxuICAgICAgKSB7XG4gICAgICAgIGNvbnN0IHN0YXJ0ID1cbiAgICAgICAgICAod2lkdGhSYW5nZSAqIChNYXRoLm1heChhbm5bJ3N0YXJ0J10sIHN0YXJ0VGltZSkgLSBzdGFydFRpbWUpKSAvXG4gICAgICAgICAgdGltZVJhbmdlO1xuICAgICAgICBjb25zdCBlbmQgPVxuICAgICAgICAgICh3aWR0aFJhbmdlICogKE1hdGgubWluKGFublsnZW5kJ10sIGVuZFRpbWUpIC0gc3RhcnRUaW1lKSkgL1xuICAgICAgICAgIHRpbWVSYW5nZTtcblxuICAgICAgICBhbm5vdGF0aW9uc1RvRHJhdy5wdXNoKHtcbiAgICAgICAgICBzdGFydDogc3RhcnRYICsgc3RhcnQsXG4gICAgICAgICAgd2lkdGg6IGVuZCAtIHN0YXJ0LFxuICAgICAgICAgIHRhZ0luZGV4ZXM6IGFubi50YWdzLm1hcCh0ID0+IHRoaXMudGFncy5pbmRleE9mKHQpKSxcbiAgICAgICAgICBpbmRleDogaSxcbiAgICAgICAgfSk7XG4gICAgICB9XG4gICAgfVxuXG4gICAgcmV0dXJuIGFubm90YXRpb25zVG9EcmF3O1xuICB9XG5cbiAgZHJhd0Fubm90YXRpb25zKHN0YXJ0VGltZTogbnVtYmVyLCBlbmRUaW1lOiBudW1iZXIpIHtcbiAgICBjb25zdCBjdHggPSB0aGlzLmNhbnZhcy5nZXRDb250ZXh0KCcyZCcpO1xuXG4gICAgaWYgKCFjdHgpIHtcbiAgICAgIGNvbnNvbGUuZXJyb3IoJ0ZhaWxlZCB0byBnZXQgMkQgY29udGV4dCcpO1xuICAgICAgcmV0dXJuO1xuICAgIH1cblxuICAgIGNvbnN0IGhlaWdodCA9IHRoaXMuY2FudmFzLmhlaWdodDtcbiAgICBjb25zdCBpbmRpY2F0b3JQYWRkaW5nID0gMjtcbiAgICBjb25zdCBpbmRpY2F0b3JIZWlnaHQgPSA1O1xuXG4gICAgY29uc3QgYW5ub3RhdGlvbnNUb0RyYXcgPSB0aGlzLmdldEFubm90YXRpb25zVG9EcmF3KHN0YXJ0VGltZSwgZW5kVGltZSk7XG5cbiAgICBmb3IgKGxldCBpID0gMDsgaSA8IGFubm90YXRpb25zVG9EcmF3Lmxlbmd0aDsgaSsrKSB7XG4gICAgICBjb25zdCBhbm4gPSBhbm5vdGF0aW9uc1RvRHJhd1tpXTtcblxuICAgICAgY3R4LmZpbGxTdHlsZSA9IGAjNzg5MDlDJHthbm4uaW5kZXggPT0gdGhpcy5zZWxlY3RlZEFubkluZGV4ID8gJzQ0JyA6ICcyMid9YDtcbiAgICAgIGN0eC5maWxsUmVjdChhbm4uc3RhcnQsIDAsIGFubi53aWR0aCwgaGVpZ2h0KTtcblxuICAgICAgZm9yIChsZXQgaSA9IDA7IGkgPCBhbm4udGFnSW5kZXhlcy5sZW5ndGg7IGkrKykge1xuICAgICAgICBjdHguZmlsbFN0eWxlID0gdGhpcy5nZXRUYWdDb2xvcihhbm4udGFnSW5kZXhlc1tpXSk7XG4gICAgICAgIGN0eC5maWxsUmVjdChcbiAgICAgICAgICBhbm4uc3RhcnQgKyBpbmRpY2F0b3JQYWRkaW5nLFxuICAgICAgICAgIGluZGljYXRvclBhZGRpbmcgKyBpICogaW5kaWNhdG9ySGVpZ2h0LFxuICAgICAgICAgIGFubi53aWR0aCAtIDIgKiBpbmRpY2F0b3JQYWRkaW5nLFxuICAgICAgICAgIGluZGljYXRvckhlaWdodCAtIGluZGljYXRvclBhZGRpbmdcbiAgICAgICAgKTtcbiAgICAgIH1cblxuICAgICAgaWYgKHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA9PSBhbm4uaW5kZXgpIHtcbiAgICAgICAgY3R4LmxpbmVDYXAgPSAncm91bmQnO1xuICAgICAgICBjdHguc3Ryb2tlU3R5bGUgPSAnIzc4OTA5Qyc7XG4gICAgICAgIGN0eC5saW5lV2lkdGggPSA0O1xuXG4gICAgICAgIC8vIExlZnQgaGFuZGxlXG4gICAgICAgIGN0eC5iZWdpblBhdGgoKTtcbiAgICAgICAgY3R4Lm1vdmVUbyhhbm4uc3RhcnQgLSA0LCBoZWlnaHQgLyAyIC0gMTIpO1xuICAgICAgICBjdHgubGluZVRvKGFubi5zdGFydCAtIDQsIGhlaWdodCAvIDIgKyAxMik7XG4gICAgICAgIGN0eC5zdHJva2UoKTtcblxuICAgICAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgICAgIGN0eC5tb3ZlVG8oYW5uLnN0YXJ0ICsgNCwgaGVpZ2h0IC8gMiAtIDEyKTtcbiAgICAgICAgY3R4LmxpbmVUbyhhbm4uc3RhcnQgKyA0LCBoZWlnaHQgLyAyICsgMTIpO1xuICAgICAgICBjdHguc3Ryb2tlKCk7XG5cbiAgICAgICAgLy8gUmlnaHQgaGFuZGxlXG4gICAgICAgIGN0eC5iZWdpblBhdGgoKTtcbiAgICAgICAgY3R4Lm1vdmVUbyhhbm4uc3RhcnQgKyBhbm4ud2lkdGggLSA0LCBoZWlnaHQgLyAyIC0gMTIpO1xuICAgICAgICBjdHgubGluZVRvKGFubi5zdGFydCArIGFubi53aWR0aCAtIDQsIGhlaWdodCAvIDIgKyAxMik7XG4gICAgICAgIGN0eC5zdHJva2UoKTtcblxuICAgICAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgICAgIGN0eC5tb3ZlVG8oYW5uLnN0YXJ0ICsgYW5uLndpZHRoICsgNCwgaGVpZ2h0IC8gMiAtIDEyKTtcbiAgICAgICAgY3R4LmxpbmVUbyhhbm4uc3RhcnQgKyBhbm4ud2lkdGggKyA0LCBoZWlnaHQgLyAyICsgMTIpO1xuICAgICAgICBjdHguc3Ryb2tlKCk7XG4gICAgICB9XG4gICAgfVxuICB9XG5cbiAgY2xlYXJGcmFtZSgpIHtcbiAgICBjb25zdCBjdHggPSB0aGlzLmNhbnZhcy5nZXRDb250ZXh0KCcyZCcpO1xuICAgIGNvbnN0IHdpZHRoID0gdGhpcy5jYW52YXMud2lkdGg7XG4gICAgY29uc3QgaGVpZ2h0ID0gdGhpcy5jYW52YXMuaGVpZ2h0O1xuXG4gICAgaWYgKCFjdHgpIHtcbiAgICAgIGNvbnNvbGUuZXJyb3IoJ0ZhaWxlZCB0byBnZXQgMkQgY29udGV4dCcpO1xuICAgICAgcmV0dXJuO1xuICAgIH1cblxuICAgIGN0eC5jbGVhclJlY3QoMCwgMCwgd2lkdGgsIGhlaWdodCk7XG5cbiAgICBjdHguc3Ryb2tlU3R5bGUgPSAnIzYwN2Q4Yic7XG5cbiAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgY3R4Lm1vdmVUbygwLCBoZWlnaHQgLyAyKTtcbiAgICBjdHgubGluZVRvKHdpZHRoLCBoZWlnaHQgLyAyKTtcbiAgICBjdHguc3Ryb2tlKCk7XG5cbiAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgY3R4Lm1vdmVUbyh3aWR0aCAvIDIsIDApO1xuICAgIGN0eC5saW5lVG8od2lkdGggLyAyLCBoZWlnaHQpO1xuICAgIGN0eC5zdHJva2UoKTtcbiAgfVxuXG4gIHN5bmNUaW1lQ2hhbmdlZCgpIHtcbiAgICB0aGlzLmN1cnJlbnRUaW1lID0gdGhpcy5tb2RlbC5nZXQoJ3N5bmNfdGltZScpO1xuICB9XG5cbiAgaXNSdW5uaW5nQ2hhbmdlZCgpIHt9XG5cbiAgcmVuZGVyKCkge1xuICAgIHRoaXMubW9kZWwub24oJ2NoYW5nZTpzeW5jX3RpbWUnLCB0aGlzLnN5bmNUaW1lQ2hhbmdlZC5iaW5kKHRoaXMpKTtcbiAgICB0aGlzLm1vZGVsLm9uKCdjaGFuZ2U6aXNfcnVubmluZycsIHRoaXMuaXNSdW5uaW5nQ2hhbmdlZC5iaW5kKHRoaXMpKTtcblxuICAgIHRoaXMuc3RlcCA9IHRoaXMuc3RlcC5iaW5kKHRoaXMpO1xuICAgIHRoaXMuYW5pbWF0aW9uRnJhbWVSZXF1ZXN0SWQgPSByZXF1ZXN0QW5pbWF0aW9uRnJhbWUodGhpcy5zdGVwKTtcbiAgfVxuXG4gIGRlc3Ryb3koKSB7XG4gICAgY2FuY2VsQW5pbWF0aW9uRnJhbWUodGhpcy5hbmltYXRpb25GcmFtZVJlcXVlc3RJZCEpO1xuICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IHtcbiAgcmVuZGVyKHByb3BzOiBSZW5kZXJQcm9wczxUaW1lcnNlcmllc1dpZGdldE1vZGVsPikge1xuICAgIGNvbnN0IHdpZGdldCA9IG5ldyBUaW1lc2VyaWVzV2lkZ2V0KHByb3BzKTtcbiAgICB3aWRnZXQucmVuZGVyKCk7XG4gICAgcmV0dXJuICgpID0+IHdpZGdldC5kZXN0cm95KCk7XG4gIH0sXG59O1xuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUFBOzs7QUNtQ0EsSUFBTSxtQkFBTixNQUF1QjtBQUFBLEVBcUNyQixZQUFZLEVBQUUsT0FBTyxHQUFHLEdBQXdDO0FBMUJoRSw0QkFBdUMsQ0FBQztBQUd4Qyx1Q0FBMEQ7QUFDMUQsbUNBQXlDO0FBR3pDLGtCQUF5QixDQUFDO0FBRzFCLHVCQUE0QixDQUFDO0FBQzdCLGdCQUFpQixDQUFDO0FBRWxCLDRCQUFtQjtBQUNuQiw0QkFBa0M7QUFDbEMsa0NBR1c7QUFDWCw4QkFLVztBQUdULFNBQUssUUFBUTtBQUNiLFNBQUssS0FBSztBQUNWLE9BQUcsWUFBWTtBQUVmLFNBQUssU0FBUyxHQUFHLGNBQWMsU0FBUztBQUN4QyxTQUFLLE9BQU8saUJBQWlCLGFBQWEsS0FBSyxnQkFBZ0IsS0FBSyxJQUFJLENB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RyxTQUFTLElBQUksRUFBRTtBQUN6QyxZQUFJLE9BQU8sSUFBSSxRQUFRLEdBQUcsU0FBUyxJQUFJLEVBQUU7QUFDekMsWUFBSSxPQUFPO0FBR1gsWUFBSSxVQUFVO0FBQ2QsWUFBSSxPQUFPLElBQUksUUFBUSxJQUFJLFFBQVEsR0FBRyxTQUFTLElBQUksRUFBRTtBQUNyRCxZQUFJLE9BQU8sSUFBSSxRQUFRLElBQUksUUFBUSxHQUFHLFNBQVMsSUFBSSxFQUFFO0FBQ3JELFlBQUksT0FBTztBQUVYLFlBQUksVUFBVTtBQUNkLFlBQUksT0FBTyxJQUFJLFFBQVEsSUFBSSxRQUFRLEdBQUcsU0FBUyxJQUFJLEVBQUU7QUFDckQsWUFBSSxPQUFPLElBQUksUUFBUSxJQUFJLFFBQVEsR0FBRyxTQUFTLElBQUksRUFBRTtBQUNyRCxZQUFJLE9BQU87QUFBQSxNQUNiO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFBQSxFQUVBLGFBQWE7QUFDWCxVQUFNLE1BQU0sS0FBSyxPQUFPLFdBQVcsSUFBSTtBQUN2QyxVQUFNLFFBQVEsS0FBSyxPQUFPO0FBQzFCLFVBQU0sU0FBUyxLQUFLLE9BQU87QUFFM0IsUUFBSSxDQUFDLEtBQUs7QUFDUixjQUFRLE1BQU0sMEJBQTBCO0FBQ3hDO0FBQUEsSUFDRjtBQUVBLFFBQUksVUFBVSxHQUFHLEdBQUcsT0FBTyxNQUFNO0FBRWpDLFFBQUksY0FBYztBQUVsQixRQUFJLFVBQVU7QUFDZCxRQUFJLE9BQU8sR0FBRyxTQUFTLENBQUM7QUFDeEIsUUFBSSxPQUFPLE9BQU8sU0FBUyxDQUFDO0FBQzVCLFFBQUksT0FBTztBQUVYLFFBQUksVUFBVTtBQUNkLFFBQUksT0FBTyxRQUFRLEdBQUcsQ0FBQztBQUN2QixRQUFJLE9BQU8sUUFBUSxHQUFHLE1BQU07QUFDNUIsUUFBSSxPQUFPO0FBQUEsRUFDYjtBQUFBLEVBRUEsa0JBQWtCO0FBQ2hCLFNBQUssY0FBYyxLQUFLLE1BQU0sSUFBSSxXQUFXO0FBQUEsRUFDL0M7QUFBQSxFQUVBLG1CQUFtQjtBQUFBLEVBQUM7QUFBQSxFQUVwQixTQUFTO0FBQ1AsU0FBSyxNQUFNLEdBQUcsb0JBQW9CLEtBQUssZ0JBQWdCLEtBQUssSUFBSSxDQUFDO0FBQ2pFLFNBQUssTUFBTSxHQUFHLHFCQUFxQixLQUFLLGlCQUFpQixLQUFLLElBQUksQ0FBQztBQUVuRSxTQUFLLE9BQU8sS0FBSyxLQUFLLEtBQUssSUFBSTtBQUMvQixTQUFLLDBCQUEwQixzQkFBc0IsS0FBSyxJQUFJO0FBQUEsRUFDaEU7QUFBQSxFQUVBLFVBQVU7QUFDUix5QkFBcUIsS0FBSyx1QkFBd0I7QUFBQSxFQUNwRDtBQUNGO0FBRUEsSUFBT0MsNkJBQVE7QUFBQSxFQUNiLE9BQU8sT0FBNEM7QUFDakQsVUFBTSxTQUFTLElBQUksaUJBQWlCLEtBQUs7QUFDekMsV0FBTyxPQUFPO0FBQ2QsV0FBTyxNQUFNLE9BQU8sUUFBUTtBQUFBLEVBQzlCO0FBQ0Y7IiwKICAibmFtZXMiOiBbImkiLCAidGltZXNlcmllc193aWRnZXRfZGVmYXVsdCJdCn0K
