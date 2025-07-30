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
    for (const tag of this.tags) {
      const label = document.createElement("label");
      const inputCheckbox = document.createElement("input");
      const labelText = document.createTextNode(tag);
      inputCheckbox.type = "checkbox";
      inputCheckbox.value = tag;
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
          color: "#607D8B",
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
    const indicatorPadding = 1;
    const indicatorHeight = 5;
    const annotationsToDraw = this.getAnnotationsToDraw(startTime, endTime);
    for (let i = 0; i < annotationsToDraw.length; i++) {
      const ann = annotationsToDraw[i];
      let color = ann.color;
      let transparency = "22";
      if (this.selectedAnnIndex != null) {
        color = ann.index == this.selectedAnnIndex ? ann.color : "#78909C";
        transparency = ann.index == this.selectedAnnIndex ? "44" : "22";
      }
      ctx.fillStyle = color + transparency;
      ctx.fillRect(ann.start, 0, ann.width, height);
      ctx.fillStyle = color;
      ctx.fillRect(
        ann.start + indicatorPadding,
        indicatorPadding,
        ann.width - 2 * indicatorPadding,
        indicatorHeight - indicatorPadding
      );
      if (this.selectedAnnIndex == ann.index) {
        ctx.lineCap = "round";
        ctx.strokeStyle = color;
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
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLi4vLi4vLi4vZnJvbnRlbmQvdGVtcGxhdGVzL3RpbWVzZXJpZXNfd2lkZ2V0Lmh0bWwiLCAiLi4vLi4vLi4vZnJvbnRlbmQvdGltZXNlcmllc193aWRnZXQudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbIjxkaXYgY2xhc3M9XCJ3aWRnZXQgdGltZXNlcmllcy13aWRnZXRcIj5cbiAgPGRpdiBjbGFzcz1cImhlYWRlclwiPlxuICAgIDxzcGFuIGNsYXNzPVwidGl0bGVcIiBpZD1cInRpdGxlXCI+PC9zcGFuPlxuICAgIDxkaXYgY2xhc3M9XCJsZWdlbmRcIiBpZD1cImxlZ2VuZFwiPjwvZGl2PlxuICA8L2Rpdj5cbiAgPGRpdiBjbGFzcz1cImdyYXBoXCIgaWQ9XCJjYW52YXMtaG9sZGVyXCI+XG4gICAgPGNhbnZhcyBpZD1cImNhbnZhc1wiPjwvY2FudmFzPlxuICA8L2Rpdj5cbiAgPGRpdiBjbGFzcz1cImNvbnRyb2xzXCI+XG4gICAgPGRpdiBjbGFzcz1cImxlZnRcIj5cbiAgICAgIDxkaXY+XG4gICAgICAgIDxidXR0b24gaWQ9XCJidG5BZGRcIj48L2J1dHRvbj5cbiAgICAgICAgPGJ1dHRvbiBpZD1cImJ0bkRlbGV0ZVwiPjwvYnV0dG9uPlxuICAgICAgPC9kaXY+XG4gICAgICA8ZGl2IGNsYXNzPVwiZHJvcGRvd25cIj5cbiAgICAgICAgPGJ1dHRvbiBjbGFzcz1cImRyb3BidG5cIiBpZD1cImJ0blRvZ2dsZVRhZ3NMaXN0XCI+XG4gICAgICAgICAgRWRpdCBUYWdzXG4gICAgICAgIDwvYnV0dG9uPlxuICAgICAgICA8ZGl2IGlkPVwidGFnc0xpc3RcIiBjbGFzcz1cImRyb3Bkb3duLWNvbnRlbnRcIj48L2Rpdj5cbiAgICAgIDwvZGl2PlxuICAgIDwvZGl2PlxuICAgIDxkaXYgY2xhc3M9XCJyaWdodFwiPlxuICAgICAgPGJ1dHRvbiBpZD1cImJ0blpvb21JblwiPjwvYnV0dG9uPlxuICAgICAgPGJ1dHRvbiBpZD1cImJ0blpvb21PdXRcIj48L2J1dHRvbj5cbiAgICA8L2Rpdj5cbiAgPC9kaXY+XG48L2Rpdj5cbiIsICJpbXBvcnQgdHlwZSB7IEFueU1vZGVsLCBSZW5kZXJQcm9wcyB9IGZyb20gJ0Bhbnl3aWRnZXQvdHlwZXMnO1xuaW1wb3J0ICcuL3N0eWxlcy93aWRnZXQuY3NzJztcbmltcG9ydCAnLi9zdHlsZXMvdGltZXNlcmllc193aWRnZXQuY3NzJztcbmltcG9ydCB0aW1lc2VyaWVzVGVtcGxhdGUgZnJvbSAnLi90ZW1wbGF0ZXMvdGltZXNlcmllc193aWRnZXQuaHRtbCc7XG5cbnR5cGUgQW5ub3RhdGlvbiA9IHtcbiAgc3RhcnQ6IG51bWJlcjtcbiAgZW5kOiBudW1iZXI7XG4gIHRhZ3M6IHN0cmluZ1tdO1xufTtcblxudHlwZSBZUmFuZ2UgPSB7XG4gIG1pbjogbnVtYmVyIHwgbnVsbDtcbiAgbWF4OiBudW1iZXIgfCBudWxsO1xufTtcblxuaW50ZXJmYWNlIFRpbWVyc2VyaWVzV2lkZ2V0TW9kZWwge1xuICBpc19ydW5uaW5nOiBib29sZWFuO1xuICBzeW5jX3RpbWU6IG51bWJlcjtcbiAgdGltZXM6IEZsb2F0NjRBcnJheTtcbiAgdmFsdWVzOiBGbG9hdDY0QXJyYXk7XG4gIHRhZ3M6IHN0cmluZ1tdO1xuICBhbm5vdGF0aW9uczogQW5ub3RhdGlvbltdO1xuICBjaGFubmVsX25hbWVzOiBzdHJpbmdbXTtcbiAgdGl0bGU6IHN0cmluZztcbiAgeV9yYW5nZTogWVJhbmdlO1xuICB4X3JhbmdlOiBudW1iZXI7XG4gIGljb25zOiB7XG4gICAgYWRkOiBzdHJpbmc7XG4gICAgZGVsZXRlOiBzdHJpbmc7XG4gICAgem9vbV9pbjogc3RyaW5nO1xuICAgIHpvb21fb3V0OiBzdHJpbmc7XG4gIH07XG59XG5cbmNsYXNzIFRpbWVzZXJpZXNXaWRnZXQge1xuICBlbDogSFRNTEVsZW1lbnQ7XG4gIG1vZGVsOiBBbnlNb2RlbDxUaW1lcnNlcmllc1dpZGdldE1vZGVsPjtcblxuICBjYW52YXM6IEhUTUxDYW52YXNFbGVtZW50O1xuICBidG5BZGQ6IEhUTUxCdXR0b25FbGVtZW50O1xuICBidG5EZWxldGU6IEhUTUxCdXR0b25FbGVtZW50O1xuICBidG5ab29tSW46IEhUTUxCdXR0b25FbGVtZW50O1xuICBidG5ab29tT3V0OiBIVE1MQnV0dG9uRWxlbWVudDtcbiAgYnRuVG9nZ2xlVGFnc0xpc3Q6IEhUTUxCdXR0b25FbGVtZW50O1xuICB0YWdzTGlzdDogSFRNTERpdkVsZW1lbnQ7XG4gIHRhZ0lucHV0RWxlbWVudHM6IEhUTUxJbnB1dEVsZW1lbnRbXSA9IFtdO1xuXG4gIGN1cnJlbnRUaW1lOiBudW1iZXI7XG4gIGxhc3RBbmltYXRpb25GcmFtZVRpbWVzdGFtcDogRE9NSGlnaFJlc1RpbWVTdGFtcCB8IG51bGwgPSBudWxsO1xuICBhbmltYXRpb25GcmFtZVJlcXVlc3RJZDogbnVtYmVyIHwgbnVsbCA9IG51bGw7XG5cbiAgdGltZXM6IEZsb2F0NjRBcnJheTtcbiAgdmFsdWVzOiBGbG9hdDY0QXJyYXlbXSA9IFtdO1xuICBudW1DaGFubmVsczogbnVtYmVyO1xuICB5UmFuZ2U6IFlSYW5nZTtcbiAgYW5ub3RhdGlvbnM6IEFubm90YXRpb25bXSA9IFtdO1xuICB0YWdzOiBzdHJpbmdbXSA9IFtdO1xuXG4gIHdpbmRvd19zaXplX2luX3MgPSA1O1xuICBzZWxlY3RlZEFubkluZGV4OiBudW1iZXIgfCBudWxsID0gbnVsbDtcbiAgc2VsZWN0ZWRSZXNpemluZ0hhbmRsZToge1xuICAgIGFubkluZGV4OiBudW1iZXI7XG4gICAgc2lkZTogJ2xlZnQnIHwgJ3JpZ2h0JztcbiAgfSB8IG51bGwgPSBudWxsO1xuICBzZWxlY3RlZE1vdmVIYW5kbGU6IHtcbiAgICBhbm5JbmRleDogbnVtYmVyO1xuICAgIGdyYWJYOiBudW1iZXI7XG4gICAgYW5uU3RhcnQ6IG51bWJlcjtcbiAgICBhbm5FbmQ6IG51bWJlcjtcbiAgfSB8IG51bGwgPSBudWxsO1xuXG4gIGNvbnN0cnVjdG9yKHsgbW9kZWwsIGVsIH06IFJlbmRlclByb3BzPFRpbWVyc2VyaWVzV2lkZ2V0TW9kZWw+KSB7XG4gICAgdGhpcy5tb2RlbCA9IG1vZGVsO1xuICAgIHRoaXMuZWwgPSBlbDtcbiAgICBlbC5pbm5lckhUTUwgPSB0aW1lc2VyaWVzVGVtcGxhdGU7XG5cbiAgICB0aGlzLmNhbnZhcyA9IGVsLnF1ZXJ5U2VsZWN0b3IoJyNjYW52YXMnKSE7XG4gICAgdGhpcy5jYW52YXMuYWRkRXZlbnRMaXN0ZW5lcignbW91c2Vkb3duJywgdGhpcy5jYW52YXNNb3VzZURvd24uYmluZCh0aGlzKSk7XG4gICAgdGhpcy5jYW52YXMuYWRkRXZlbnRMaXN0ZW5lcignbW91c2Vtb3ZlJywgdGhpcy5jYW52YXNNb3VzZU1vdmUuYmluZCh0aGlzKSk7XG4gICAgdGhpcy5jYW52YXMuYWRkRXZlbnRMaXN0ZW5lcignbW91c2V1cCcsIHRoaXMuY2FudmFzTW91c2VVcC5iaW5kKHRoaXMpKTtcblxuICAgIHRoaXMuYnRuQWRkID0gZWwucXVlcnlTZWxlY3RvcignI2J0bkFkZCcpITtcbiAgICB0aGlzLmJ0bkFkZC5pbm5lckhUTUwgPSB0aGlzLm1vZGVsLmdldCgnaWNvbnMnKS5hZGQ7XG4gICAgdGhpcy5idG5BZGQuYWRkRXZlbnRMaXN0ZW5lcignY2xpY2snLCB0aGlzLmJ0bkFkZENsaWNrZWQuYmluZCh0aGlzKSk7XG5cbiAgICB0aGlzLmJ0bkRlbGV0ZSA9IGVsLnF1ZXJ5U2VsZWN0b3IoJyNidG5EZWxldGUnKSE7XG4gICAgdGhpcy5idG5EZWxldGUuaW5uZXJIVE1MID0gdGhpcy5tb2RlbC5nZXQoJ2ljb25zJykuZGVsZXRlO1xuICAgIHRoaXMuYnRuRGVsZXRlLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgdGhpcy5idG5EZWxldGVDbGlja2VkLmJpbmQodGhpcykpO1xuXG4gICAgdGhpcy5idG5ab29tSW4gPSBlbC5xdWVyeVNlbGVjdG9yKCcjYnRuWm9vbUluJykhO1xuICAgIHRoaXMuYnRuWm9vbUluLmlubmVySFRNTCA9IHRoaXMubW9kZWwuZ2V0KCdpY29ucycpLnpvb21faW47XG4gICAgdGhpcy5idG5ab29tSW4uYWRkRXZlbnRMaXN0ZW5lcignY2xpY2snLCB0aGlzLmJ0blpvb21JbkNsaWNrZWQuYmluZCh0aGlzKSk7XG5cbiAgICB0aGlzLmJ0blpvb21PdXQgPSBlbC5xdWVyeVNlbGVjdG9yKCcjYnRuWm9vbU91dCcpITtcbiAgICB0aGlzLmJ0blpvb21PdXQuaW5uZXJIVE1MID0gdGhpcy5tb2RlbC5nZXQoJ2ljb25zJykuem9vbV9vdXQ7XG4gICAgdGhpcy5idG5ab29tT3V0LmFkZEV2ZW50TGlzdGVuZXIoXG4gICAgICAnY2xpY2snLFxuICAgICAgdGhpcy5idG5ab29tT3V0Q2xpY2tlZC5iaW5kKHRoaXMpXG4gICAgKTtcblxuICAgIHRoaXMuYnRuVG9nZ2xlVGFnc0xpc3QgPSBlbC5xdWVyeVNlbGVjdG9yKCcjYnRuVG9nZ2xlVGFnc0xpc3QnKSE7XG4gICAgdGhpcy5idG5Ub2dnbGVUYWdzTGlzdC5hZGRFdmVudExpc3RlbmVyKFxuICAgICAgJ2NsaWNrJyxcbiAgICAgIHRoaXMudG9nZ2xlVGFnc0xpc3QuYmluZCh0aGlzKVxuICAgICk7XG5cbiAgICB0aGlzLnRhZ3NMaXN0ID0gZWwucXVlcnlTZWxlY3RvcignI3RhZ3NMaXN0JykhO1xuXG4gICAgdGhpcy5jdXJyZW50VGltZSA9IHRoaXMubW9kZWwuZ2V0KCdzeW5jX3RpbWUnKTtcblxuICAgIGNvbnN0IHRpbWVzX2J5dGVzID0gdGhpcy5tb2RlbC5nZXQoJ3RpbWVzJyk7XG4gICAgY29uc3QgdGltZXNfYnVmZmVyID0gdGltZXNfYnl0ZXMuYnVmZmVyIHx8IHRpbWVzX2J5dGVzO1xuICAgIHRoaXMudGltZXMgPSBuZXcgRmxvYXQ2NEFycmF5KHRpbWVzX2J1ZmZlcik7XG5cbiAgICBjb25zdCB2YWx1ZXNfYnl0ZXMgPSB0aGlzLm1vZGVsLmdldCgndmFsdWVzJyk7XG4gICAgY29uc3QgdmFsdWVzX2J1ZmZlciA9IHZhbHVlc19ieXRlcy5idWZmZXIgfHwgdmFsdWVzX2J5dGVzO1xuICAgIGNvbnN0IGFsbF92YWx1ZXMgPSBuZXcgRmxvYXQ2NEFycmF5KHZhbHVlc19idWZmZXIpO1xuXG4gICAgY29uc3QgbnVtX2VsZW1lbnRzID0gdGhpcy50aW1lcy5sZW5ndGg7XG4gICAgY29uc3QgdG90YWxfdmFsdWVzX2NvdW50ID0gYWxsX3ZhbHVlcy5sZW5ndGg7XG4gICAgdGhpcy5udW1DaGFubmVscyA9IHRvdGFsX3ZhbHVlc19jb3VudCAvIG51bV9lbGVtZW50cztcblxuICAgIGZvciAobGV0IGkgPSAwOyBpIDwgdGhpcy5udW1DaGFubmVsczsgaSsrKSB7XG4gICAgICB0aGlzLnZhbHVlcy5wdXNoKFxuICAgICAgICBhbGxfdmFsdWVzLnNsaWNlKGkgKiBudW1fZWxlbWVudHMsIGkgKiBudW1fZWxlbWVudHMgKyBudW1fZWxlbWVudHMpXG4gICAgICApO1xuICAgIH1cblxuICAgIHRoaXMuYW5ub3RhdGlvbnMgPSB0aGlzLm1vZGVsLmdldCgnYW5ub3RhdGlvbnMnKTtcbiAgICB0aGlzLnlSYW5nZSA9IHRoaXMubW9kZWwuZ2V0KCd5X3JhbmdlJyk7XG4gICAgdGhpcy53aW5kb3dfc2l6ZV9pbl9zID0gdGhpcy5tb2RlbC5nZXQoJ3hfcmFuZ2UnKTtcbiAgICB0aGlzLnRhZ3MgPSB0aGlzLm1vZGVsLmdldCgndGFncycpO1xuXG4gICAgdGhpcy5wb3B1bGF0ZVRhZ3NMaXN0KCk7XG4gICAgdGhpcy5hZGRMZWdlbmQoKTtcbiAgICB0aGlzLmFkZFRpdGxlKCk7XG4gIH1cblxuICBwb3B1bGF0ZVRhZ3NMaXN0KCkge1xuICAgIGZvciAoY29uc3QgdGFnIG9mIHRoaXMudGFncykge1xuICAgICAgY29uc3QgbGFiZWwgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdsYWJlbCcpO1xuICAgICAgY29uc3QgaW5wdXRDaGVja2JveCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2lucHV0Jyk7XG4gICAgICBjb25zdCBsYWJlbFRleHQgPSBkb2N1bWVudC5jcmVhdGVUZXh0Tm9kZSh0YWcpO1xuXG4gICAgICBpbnB1dENoZWNrYm94LnR5cGUgPSAnY2hlY2tib3gnO1xuICAgICAgaW5wdXRDaGVja2JveC52YWx1ZSA9IHRhZztcbiAgICAgIGlucHV0Q2hlY2tib3guYWRkRXZlbnRMaXN0ZW5lcignY2hhbmdlJywgdGhpcy50YWdUb2dnbGVkLmJpbmQodGhpcykpO1xuXG4gICAgICBsYWJlbC5hcHBlbmRDaGlsZChpbnB1dENoZWNrYm94KTtcbiAgICAgIGxhYmVsLmFwcGVuZENoaWxkKGxhYmVsVGV4dCk7XG5cbiAgICAgIHRoaXMudGFnSW5wdXRFbGVtZW50cy5wdXNoKGlucHV0Q2hlY2tib3gpO1xuICAgICAgdGhpcy50YWdzTGlzdC5hcHBlbmRDaGlsZChsYWJlbCk7XG4gICAgfVxuICB9XG5cbiAgdGFnVG9nZ2xlZChlOiBFdmVudCkge1xuICAgIGlmICh0aGlzLnNlbGVjdGVkQW5uSW5kZXggPT0gbnVsbCkgcmV0dXJuO1xuXG4gICAgY29uc3QgdGFyZ2V0ID0gZS50YXJnZXQgYXMgSFRNTElucHV0RWxlbWVudDtcbiAgICBjb25zdCBhbm4gPSB0aGlzLmFubm90YXRpb25zW3RoaXMuc2VsZWN0ZWRBbm5JbmRleF07XG5cbiAgICBpZiAodGFyZ2V0LmNoZWNrZWQpIHtcbiAgICAgIGFubi50YWdzLnB1c2godGFyZ2V0LnZhbHVlKTtcbiAgICB9IGVsc2Uge1xuICAgICAgYW5uLnRhZ3MgPSBhbm4udGFncy5maWx0ZXIodCA9PiB0ICE9PSB0YXJnZXQudmFsdWUpO1xuICAgIH1cblxuICAgIHRoaXMuc3luY0Fubm90YXRpb25zKCk7XG4gIH1cblxuICBjYW52YXNNb3VzZURvd24oZTogTW91c2VFdmVudCkge1xuICAgIGlmICh0aGlzLmNoZWNrRm9ySGFuZGxlU2VsZWN0aW9uKGUub2Zmc2V0WCkpIHtcbiAgICAgIHJldHVybjtcbiAgICB9XG5cbiAgICBpZiAodGhpcy5jaGVja0ZvckFublNlbGVjdGlvbihlLm9mZnNldFgpKSB7XG4gICAgICB0aGlzLnVwZGF0ZVRhZ0NoZWNrYm94ZXMoKTtcbiAgICAgIHRoaXMuYnRuVG9nZ2xlVGFnc0xpc3QuY2xhc3NMaXN0LmFkZCgnc2hvdycpO1xuICAgIH0gZWxzZSB7XG4gICAgICB0aGlzLmJ0blRvZ2dsZVRhZ3NMaXN0LmNsYXNzTGlzdC5yZW1vdmUoJ3Nob3cnKTtcbiAgICAgIHRoaXMudGFnc0xpc3QuY2xhc3NMaXN0LnJlbW92ZSgnc2hvdycpO1xuICAgIH1cbiAgfVxuXG4gIHVwZGF0ZVRhZ0NoZWNrYm94ZXMoKSB7XG4gICAgaWYgKHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA9PSBudWxsKSByZXR1cm47XG4gICAgY29uc3QgdGFncyA9IHRoaXMuYW5ub3RhdGlvbnNbdGhpcy5zZWxlY3RlZEFubkluZGV4XS50YWdzO1xuXG4gICAgZm9yIChjb25zdCBjaGVja2JveCBvZiB0aGlzLnRhZ0lucHV0RWxlbWVudHMpIHtcbiAgICAgIGNoZWNrYm94LmNoZWNrZWQgPSB0YWdzLmluY2x1ZGVzKGNoZWNrYm94LnZhbHVlKTtcbiAgICB9XG4gIH1cblxuICBjYW52YXNNb3VzZU1vdmUoZTogTW91c2VFdmVudCkge1xuICAgIGlmICh0aGlzLnNlbGVjdGVkUmVzaXppbmdIYW5kbGUgIT0gbnVsbCkge1xuICAgICAgdGhpcy5yZXNpemVBbm5vdGF0aW9uKGUub2Zmc2V0WCk7XG4gICAgfSBlbHNlIGlmICh0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZSAhPSBudWxsKSB7XG4gICAgICB0aGlzLm1vdmVBbm5vdGF0aW9uKGUub2Zmc2V0WCk7XG4gICAgfVxuICB9XG5cbiAgcmVzaXplQW5ub3RhdGlvbihtb3VzZVg6IG51bWJlcikge1xuICAgIGlmICh0aGlzLnNlbGVjdGVkUmVzaXppbmdIYW5kbGUgPT0gbnVsbCkgcmV0dXJuO1xuXG4gICAgY29uc3Qgd2lkdGggPSB0aGlzLmNhbnZhcy53aWR0aDtcbiAgICBjb25zdCB0aW1lID1cbiAgICAgIHRoaXMuY3VycmVudFRpbWUgKyAodGhpcy53aW5kb3dfc2l6ZV9pbl9zICogKG1vdXNlWCAtIHdpZHRoIC8gMikpIC8gd2lkdGg7XG5cbiAgICBpZiAodGhpcy5zZWxlY3RlZFJlc2l6aW5nSGFuZGxlLnNpZGUgPT0gJ2xlZnQnKSB7XG4gICAgICB0aGlzLmFubm90YXRpb25zW3RoaXMuc2VsZWN0ZWRSZXNpemluZ0hhbmRsZS5hbm5JbmRleF0uc3RhcnQgPSB0aW1lO1xuICAgIH0gZWxzZSB7XG4gICAgICB0aGlzLmFubm90YXRpb25zW3RoaXMuc2VsZWN0ZWRSZXNpemluZ0hhbmRsZS5hbm5JbmRleF0uZW5kID0gdGltZTtcbiAgICB9XG4gIH1cblxuICBtb3ZlQW5ub3RhdGlvbihtb3VzZVg6IG51bWJlcikge1xuICAgIGlmICh0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZSA9PSBudWxsKSByZXR1cm47XG5cbiAgICBjb25zdCB3aWR0aCA9IHRoaXMuY2FudmFzLndpZHRoO1xuICAgIGNvbnN0IG9mZnNldFRpbWUgPVxuICAgICAgKHRoaXMud2luZG93X3NpemVfaW5fcyAqIChtb3VzZVggLSB0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZS5ncmFiWCkpIC9cbiAgICAgIHdpZHRoO1xuICAgIHRoaXMuYW5ub3RhdGlvbnNbdGhpcy5zZWxlY3RlZE1vdmVIYW5kbGUuYW5uSW5kZXhdLnN0YXJ0ID1cbiAgICAgIHRoaXMuc2VsZWN0ZWRNb3ZlSGFuZGxlLmFublN0YXJ0ICsgb2Zmc2V0VGltZTtcbiAgICB0aGlzLmFubm90YXRpb25zW3RoaXMuc2VsZWN0ZWRNb3ZlSGFuZGxlLmFubkluZGV4XS5lbmQgPVxuICAgICAgdGhpcy5zZWxlY3RlZE1vdmVIYW5kbGUuYW5uRW5kICsgb2Zmc2V0VGltZTtcbiAgfVxuXG4gIGNhbnZhc01vdXNlVXAoKSB7XG4gICAgdGhpcy5zZWxlY3RlZFJlc2l6aW5nSGFuZGxlID0gbnVsbDtcbiAgICB0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZSA9IG51bGw7XG4gICAgdGhpcy5zeW5jQW5ub3RhdGlvbnMoKTtcbiAgfVxuXG4gIGJ0bkFkZENsaWNrZWQoKSB7XG4gICAgdGhpcy5hbm5vdGF0aW9ucy5wdXNoKHtcbiAgICAgIHN0YXJ0OiB0aGlzLmN1cnJlbnRUaW1lLFxuICAgICAgZW5kOiB0aGlzLmN1cnJlbnRUaW1lICsgMC41LFxuICAgICAgdGFnczogW10sXG4gICAgfSk7XG5cbiAgICB0aGlzLnNlbGVjdGVkQW5uSW5kZXggPSB0aGlzLmFubm90YXRpb25zLmxlbmd0aCAtIDE7XG5cbiAgICB0aGlzLnN5bmNBbm5vdGF0aW9ucygpO1xuICB9XG5cbiAgYnRuRGVsZXRlQ2xpY2tlZCgpIHtcbiAgICBpZiAodGhpcy5zZWxlY3RlZEFubkluZGV4ID09IG51bGwpIHJldHVybjtcblxuICAgIHRoaXMuYW5ub3RhdGlvbnMuc3BsaWNlKHRoaXMuc2VsZWN0ZWRBbm5JbmRleCwgMSk7XG4gICAgdGhpcy5zZWxlY3RlZEFubkluZGV4ID0gbnVsbDtcblxuICAgIHRoaXMuc3luY0Fubm90YXRpb25zKCk7XG4gIH1cblxuICBidG5ab29tSW5DbGlja2VkKCkge1xuICAgIHRoaXMud2luZG93X3NpemVfaW5fcyAtPSAwLjU7XG4gIH1cblxuICBidG5ab29tT3V0Q2xpY2tlZCgpIHtcbiAgICB0aGlzLndpbmRvd19zaXplX2luX3MgKz0gMC41O1xuICB9XG5cbiAgdG9nZ2xlVGFnc0xpc3QoKSB7XG4gICAgdGhpcy50YWdzTGlzdC5jbGFzc0xpc3QudG9nZ2xlKCdzaG93Jyk7XG4gIH1cblxuICBzeW5jQW5ub3RhdGlvbnMoKSB7XG4gICAgdGhpcy5tb2RlbC5zZXQoJ2Fubm90YXRpb25zJywgW10pO1xuICAgIHRoaXMubW9kZWwuc2V0KCdhbm5vdGF0aW9ucycsIFsuLi50aGlzLmFubm90YXRpb25zXSk7XG4gICAgdGhpcy5tb2RlbC5zYXZlX2NoYW5nZXMoKTtcbiAgfVxuXG4gIGNoZWNrRm9yQW5uU2VsZWN0aW9uKG1vdXNlWDogbnVtYmVyKSB7XG4gICAgY29uc3Qgc3RhcnRUaW1lID0gdGhpcy5jdXJyZW50VGltZSAtIHRoaXMud2luZG93X3NpemVfaW5fcyAvIDI7XG4gICAgY29uc3QgZW5kVGltZSA9IHRoaXMuY3VycmVudFRpbWUgKyB0aGlzLndpbmRvd19zaXplX2luX3MgLyAyO1xuXG4gICAgY29uc3QgZHJhd25Bbm5zID0gdGhpcy5nZXRBbm5vdGF0aW9uc1RvRHJhdyhzdGFydFRpbWUsIGVuZFRpbWUpO1xuXG4gICAgdGhpcy5zZWxlY3RlZEFubkluZGV4ID0gbnVsbDtcbiAgICBmb3IgKGxldCBpID0gMDsgaSA8IGRyYXduQW5ucy5sZW5ndGg7IGkrKykge1xuICAgICAgY29uc3QgYW5uID0gZHJhd25Bbm5zW2ldO1xuICAgICAgaWYgKGFubi5zdGFydCA+IG1vdXNlWCB8fCBhbm4uc3RhcnQgKyBhbm4ud2lkdGggPCBtb3VzZVgpIGNvbnRpbnVlO1xuICAgICAgdGhpcy5zZWxlY3RlZEFubkluZGV4ID0gYW5uLmluZGV4O1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfVxuXG4gICAgcmV0dXJuIGZhbHNlO1xuICB9XG5cbiAgY2hlY2tGb3JIYW5kbGVTZWxlY3Rpb24obW91c2VYOiBudW1iZXIpIHtcbiAgICBjb25zdCBzdGFydFRpbWUgPSB0aGlzLmN1cnJlbnRUaW1lIC0gdGhpcy53aW5kb3dfc2l6ZV9pbl9zIC8gMjtcbiAgICBjb25zdCBlbmRUaW1lID0gdGhpcy5jdXJyZW50VGltZSArIHRoaXMud2luZG93X3NpemVfaW5fcyAvIDI7XG5cbiAgICBjb25zdCBkcmF3bkFubnMgPSB0aGlzLmdldEFubm90YXRpb25zVG9EcmF3KHN0YXJ0VGltZSwgZW5kVGltZSk7XG5cbiAgICB0aGlzLnNlbGVjdGVkUmVzaXppbmdIYW5kbGUgPSBudWxsO1xuICAgIHRoaXMuc2VsZWN0ZWRNb3ZlSGFuZGxlID0gbnVsbDtcbiAgICBmb3IgKGxldCBpID0gMDsgaSA8IGRyYXduQW5ucy5sZW5ndGg7IGkrKykge1xuICAgICAgY29uc3QgYW5uID0gZHJhd25Bbm5zW2ldO1xuXG4gICAgICAvLyBDaGVjayBmb3IgbGVmdCBoYW5kbGVcbiAgICAgIGlmIChNYXRoLmFicyhtb3VzZVggLSBhbm4uc3RhcnQpIDwgNikge1xuICAgICAgICB0aGlzLnNlbGVjdGVkUmVzaXppbmdIYW5kbGUgPSB7XG4gICAgICAgICAgYW5uSW5kZXg6IGFubi5pbmRleCxcbiAgICAgICAgICBzaWRlOiAnbGVmdCcsXG4gICAgICAgIH07XG4gICAgICAgIHJldHVybiB0cnVlO1xuICAgICAgfVxuXG4gICAgICAvLyBDaGVjayBmb3IgcmlnaHQgaGFuZGxlXG4gICAgICBpZiAoTWF0aC5hYnMobW91c2VYIC0gYW5uLnN0YXJ0IC0gYW5uLndpZHRoKSA8IDYpIHtcbiAgICAgICAgdGhpcy5zZWxlY3RlZFJlc2l6aW5nSGFuZGxlID0ge1xuICAgICAgICAgIGFubkluZGV4OiBhbm4uaW5kZXgsXG4gICAgICAgICAgc2lkZTogJ3JpZ2h0JyxcbiAgICAgICAgfTtcbiAgICAgICAgcmV0dXJuIHRydWU7XG4gICAgICB9XG5cbiAgICAgIC8vIE1vdmUgaGFuZGxlXG4gICAgICBpZiAobW91c2VYID4gYW5uLnN0YXJ0ICYmIG1vdXNlWCA8IGFubi5zdGFydCArIGFubi53aWR0aCkge1xuICAgICAgICB0aGlzLnNlbGVjdGVkTW92ZUhhbmRsZSA9IHtcbiAgICAgICAgICBhbm5JbmRleDogYW5uLmluZGV4LFxuICAgICAgICAgIGdyYWJYOiBtb3VzZVgsXG4gICAgICAgICAgYW5uU3RhcnQ6IHRoaXMuYW5ub3RhdGlvbnNbYW5uLmluZGV4XS5zdGFydCxcbiAgICAgICAgICBhbm5FbmQ6IHRoaXMuYW5ub3RhdGlvbnNbYW5uLmluZGV4XS5lbmQsXG4gICAgICAgIH07XG4gICAgICB9XG4gICAgfVxuXG4gICAgcmV0dXJuIGZhbHNlO1xuICB9XG5cbiAgYWRkTGVnZW5kKCkge1xuICAgIGNvbnN0IGxlZ2VuZCA9IHRoaXMuZWwucXVlcnlTZWxlY3RvcignI2xlZ2VuZCcpITtcblxuICAgIGZvciAoY29uc3QgY2hhbm5lbCBvZiB0aGlzLm1vZGVsLmdldCgnY2hhbm5lbF9uYW1lcycpKSB7XG4gICAgICBjb25zdCBjaGFubmVsSW5kZXggPSB0aGlzLm1vZGVsXG4gICAgICAgIC5nZXQoJ2NoYW5uZWxfbmFtZXMnKVxuICAgICAgICAuZmluZEluZGV4KGUgPT4gZSA9PSBjaGFubmVsKTtcbiAgICAgIGNvbnN0IGxhYmVsID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnc3BhbicpO1xuICAgICAgbGFiZWwuaW5uZXJIVE1MID0gY2hhbm5lbDtcbiAgICAgIGxhYmVsLnN0eWxlLnNldFByb3BlcnR5KCctLWxpbmUtY29sb3InLCB0aGlzLmdldFBsb3RDb2xvcihjaGFubmVsSW5kZXgpKTtcbiAgICAgIGxlZ2VuZC5hcHBlbmQobGFiZWwpO1xuICAgIH1cbiAgfVxuXG4gIGFkZFRpdGxlKCkge1xuICAgIGNvbnN0IHRpdGxlID0gdGhpcy5lbC5xdWVyeVNlbGVjdG9yKCcjdGl0bGUnKSE7XG4gICAgdGl0bGUuaW5uZXJIVE1MID0gdGhpcy5tb2RlbC5nZXQoJ3RpdGxlJyk7XG4gIH1cblxuICBnZXRQbG90Q29sb3IoY2hhbm5lbEluZGV4OiBudW1iZXIpIHtcbiAgICBjb25zdCBjb2xvcnMgPSBbXG4gICAgICAnI0Y0NDMzNicsXG4gICAgICAnIzRDQUY1MCcsXG4gICAgICAnIzIxOTZGMycsXG4gICAgICAnI0ZGRUIzQicsXG4gICAgICAnIzc5NTU0OCcsXG4gICAgICAnIzY3M0FCNycsXG4gICAgXTtcblxuICAgIGNvbnN0IGluZGV4ID0gY2hhbm5lbEluZGV4ICUgY29sb3JzLmxlbmd0aDtcblxuICAgIHJldHVybiBjb2xvcnNbaW5kZXhdO1xuICB9XG5cbiAgZ2V0VGFnQ29sb3IodGFnSW5kZXg6IG51bWJlcikge1xuICAgIGNvbnN0IGNvbG9ycyA9IFtcbiAgICAgICcjRjQ0MzM2JyxcbiAgICAgICcjM0Y1MUI1JyxcbiAgICAgICcjMDBCQ0Q0JyxcbiAgICAgICcjOUMyN0IwJyxcbiAgICAgICcjRTkxRTYzJyxcbiAgICAgICcjQ0REQzM5JyxcbiAgICAgICcjNzk1NTQ4JyxcbiAgICAgICcjRkZFQjNCJyxcbiAgICAgICcjNjA3RDhCJyxcbiAgICAgICcjMjE5NkYzJyxcbiAgICBdO1xuXG4gICAgY29uc3QgaW5kZXggPSB0YWdJbmRleCAlIGNvbG9ycy5sZW5ndGg7XG5cbiAgICByZXR1cm4gY29sb3JzW2luZGV4XTtcbiAgfVxuXG4gIHN0ZXAodGltZXN0YW1wOiBET01IaWdoUmVzVGltZVN0YW1wKSB7XG4gICAgaWYgKCF0aGlzLmxhc3RBbmltYXRpb25GcmFtZVRpbWVzdGFtcCkge1xuICAgICAgY29uc3QgY2FudmFzSG9sZGVyID0gdGhpcy5lbC5xdWVyeVNlbGVjdG9yKCcjY2FudmFzLWhvbGRlcicpITtcbiAgICAgIHRoaXMuY2FudmFzLndpZHRoID0gY2FudmFzSG9sZGVyLmNsaWVudFdpZHRoO1xuICAgICAgdGhpcy5jYW52YXMuaGVpZ2h0ID0gY2FudmFzSG9sZGVyLmNsaWVudEhlaWdodDtcbiAgICAgIHRoaXMuY2FudmFzLnN0eWxlLndpZHRoID0gJzEwMCUnO1xuICAgICAgdGhpcy5jYW52YXMuc3R5bGUuaGVpZ2h0ID0gJzEwMCUnO1xuXG4gICAgICB0aGlzLmxhc3RBbmltYXRpb25GcmFtZVRpbWVzdGFtcCA9IHRpbWVzdGFtcDtcbiAgICB9XG5cbiAgICBjb25zdCBkZWx0YSA9IHRpbWVzdGFtcCAtIHRoaXMubGFzdEFuaW1hdGlvbkZyYW1lVGltZXN0YW1wO1xuICAgIHRoaXMubGFzdEFuaW1hdGlvbkZyYW1lVGltZXN0YW1wID0gdGltZXN0YW1wO1xuXG4gICAgaWYgKHRoaXMubW9kZWwuZ2V0KCdpc19ydW5uaW5nJykpIHtcbiAgICAgIGNvbnN0IGR1cmF0aW9uID0gdGhpcy50aW1lc1t0aGlzLnRpbWVzLmxlbmd0aCAtIDFdO1xuICAgICAgdGhpcy5jdXJyZW50VGltZSA9IE1hdGgubWluKHRoaXMuY3VycmVudFRpbWUgKyBkZWx0YSAvIDEwMDAsIGR1cmF0aW9uKTtcbiAgICB9XG5cbiAgICB0aGlzLmNsZWFyRnJhbWUoKTtcbiAgICB0aGlzLmRyYXcoKTtcblxuICAgIHRoaXMuYW5pbWF0aW9uRnJhbWVSZXF1ZXN0SWQgPSByZXF1ZXN0QW5pbWF0aW9uRnJhbWUodGhpcy5zdGVwKTtcbiAgfVxuXG4gIGRyYXcoKSB7XG4gICAgY29uc3Qgc3RhcnRUaW1lID0gdGhpcy5jdXJyZW50VGltZSAtIHRoaXMud2luZG93X3NpemVfaW5fcyAvIDI7XG4gICAgY29uc3QgZW5kVGltZSA9IHRoaXMuY3VycmVudFRpbWUgKyB0aGlzLndpbmRvd19zaXplX2luX3MgLyAyO1xuXG4gICAgY29uc3Qgc3RhcnRJbmRleCA9IHRoaXMudGltZXMuZmluZEluZGV4KGUgPT4gZSA+PSBzdGFydFRpbWUpO1xuICAgIGNvbnN0IGVuZEluZGV4UGx1czEgPSB0aGlzLnRpbWVzLmZpbmRJbmRleChlID0+IGUgPiBlbmRUaW1lKTtcblxuICAgIGNvbnN0IGVuZEluZGV4ID1cbiAgICAgIGVuZEluZGV4UGx1czEgIT0gLTFcbiAgICAgICAgPyBNYXRoLm1heChlbmRJbmRleFBsdXMxIC0gMSwgMClcbiAgICAgICAgOiB0aGlzLnRpbWVzLmxlbmd0aCAtIDE7XG5cbiAgICBjb25zdCBmaXJzdFBvaW50VGltZURlbHRhID0gdGhpcy50aW1lc1tzdGFydEluZGV4XSAtIHRoaXMuY3VycmVudFRpbWU7XG4gICAgY29uc3QgbGFzdFBvaW50VGltZURlbHRhID0gdGhpcy50aW1lc1tlbmRJbmRleF0gLSB0aGlzLmN1cnJlbnRUaW1lO1xuICAgIGNvbnN0IGxlZnRPZmZzZXRQZXJjZW50YWdlID0gTWF0aC5tYXgoXG4gICAgICBmaXJzdFBvaW50VGltZURlbHRhIC8gdGhpcy53aW5kb3dfc2l6ZV9pbl9zICsgMC41LFxuICAgICAgMFxuICAgICk7XG4gICAgY29uc3QgcmlnaHRPZmZzZXRQZXJjZW50YWdlID1cbiAgICAgIGxhc3RQb2ludFRpbWVEZWx0YSAvIHRoaXMud2luZG93X3NpemVfaW5fcyArIDAuNTtcblxuICAgIHRoaXMuZHJhd0Fubm90YXRpb25zKHN0YXJ0VGltZSwgZW5kVGltZSk7XG5cbiAgICBmb3IgKGxldCBjID0gMDsgYyA8IHRoaXMubnVtQ2hhbm5lbHM7IGMrKykge1xuICAgICAgdGhpcy5kcmF3UGxvdChcbiAgICAgICAgYyxcbiAgICAgICAgc3RhcnRJbmRleCxcbiAgICAgICAgZW5kSW5kZXgsXG4gICAgICAgIGxlZnRPZmZzZXRQZXJjZW50YWdlLFxuICAgICAgICByaWdodE9mZnNldFBlcmNlbnRhZ2VcbiAgICAgICk7XG4gICAgfVxuICB9XG5cbiAgZ2V0UmFuZ2Uoc3RhcnRJbmRleDogbnVtYmVyLCBlbmRJbmRleDogbnVtYmVyKSB7XG4gICAgbGV0IG1pbiA9IHRoaXMueVJhbmdlLm1pbjtcbiAgICBsZXQgbWF4ID0gdGhpcy55UmFuZ2UubWF4O1xuXG4gICAgaWYgKG1pbiAhPSBudWxsICYmIG1heCAhPSBudWxsKSByZXR1cm4geyBtaW4sIG1heCB9O1xuXG4gICAgY29uc3QgbWlucyA9IFtdO1xuICAgIGNvbnN0IG1heHMgPSBbXTtcblxuICAgIGZvciAobGV0IGMgPSAwOyBjIDwgdGhpcy5udW1DaGFubmVsczsgYysrKSB7XG4gICAgICBpZiAobWluID09IG51bGwpIHtcbiAgICAgICAgbWlucy5wdXNoKE1hdGgubWluKC4uLnRoaXMudmFsdWVzW2NdLnNsaWNlKHN0YXJ0SW5kZXgsIGVuZEluZGV4ICsgMSkpKTtcbiAgICAgIH1cbiAgICAgIGlmIChtYXggPT0gbnVsbCkge1xuICAgICAgICBtYXhzLnB1c2goTWF0aC5tYXgoLi4udGhpcy52YWx1ZXNbY10uc2xpY2Uoc3RhcnRJbmRleCwgZW5kSW5kZXggKyAxKSkpO1xuICAgICAgfVxuICAgIH1cblxuICAgIHJldHVybiB7XG4gICAgICBtaW46IG1pbiA/IG1pbiA6IE1hdGgubWluKC4uLm1pbnMpLFxuICAgICAgbWF4OiBtYXggPyBtYXggOiBNYXRoLm1heCguLi5tYXhzKSxcbiAgICB9O1xuICB9XG5cbiAgZHJhd1Bsb3QoXG4gICAgY2hhbm5lbEluZGV4OiBudW1iZXIsXG4gICAgc3RhcnRJbmRleDogbnVtYmVyLFxuICAgIGVuZEluZGV4OiBudW1iZXIsXG4gICAgbGVmdE9mZnNldFBlcmNlbnRhZ2U6IG51bWJlcixcbiAgICByaWdodE9mZnNldFBlcmNlbnRhZ2U6IG51bWJlclxuICApIHtcbiAgICBpZiAoaXNOYU4oc3RhcnRJbmRleCkgfHwgaXNOYU4oZW5kSW5kZXgpKSByZXR1cm47XG5cbiAgICBjb25zdCBjdHggPSB0aGlzLmNhbnZhcy5nZXRDb250ZXh0KCcyZCcpO1xuICAgIGNvbnN0IHdpZHRoID0gdGhpcy5jYW52YXMud2lkdGg7XG4gICAgY29uc3QgaGVpZ2h0ID0gdGhpcy5jYW52YXMuaGVpZ2h0O1xuXG4gICAgaWYgKCFjdHgpIHtcbiAgICAgIGNvbnNvbGUuZXJyb3IoJ0ZhaWxlZCB0byBnZXQgMkQgY29udGV4dCcpO1xuICAgICAgcmV0dXJuO1xuICAgIH1cblxuICAgIGN0eC5zdHJva2VTdHlsZSA9IHRoaXMuZ2V0UGxvdENvbG9yKGNoYW5uZWxJbmRleCk7XG4gICAgY3R4LmxpbmVXaWR0aCA9IDI7XG5cbiAgICBjdHguYmVnaW5QYXRoKCk7XG5cbiAgICBjb25zdCBpbmRleFJhbmdlID0gZW5kSW5kZXggLSBzdGFydEluZGV4O1xuICAgIGNvbnN0IGZ1bGxXaWR0aFJhbmdlID0gd2lkdGg7XG4gICAgY29uc3Qgc3RhcnRYID0gbGVmdE9mZnNldFBlcmNlbnRhZ2UgKiBmdWxsV2lkdGhSYW5nZTtcbiAgICBjb25zdCBlbmRYID0gcmlnaHRPZmZzZXRQZXJjZW50YWdlICogZnVsbFdpZHRoUmFuZ2U7XG4gICAgY29uc3Qgd2lkdGhSYW5nZSA9IGVuZFggLSBzdGFydFg7XG4gICAgY29uc3QgaGVpZ2h0UmFuZ2UgPSBoZWlnaHQ7XG4gICAgY29uc3QgeyBtaW4sIG1heCB9ID0gdGhpcy5nZXRSYW5nZShzdGFydEluZGV4LCBlbmRJbmRleCk7XG4gICAgY29uc3QgeVJhbmdlID0gbWF4IC0gbWluO1xuXG4gICAgY29uc3QgdmFsdWVzID0gdGhpcy52YWx1ZXNbY2hhbm5lbEluZGV4XTtcblxuICAgIGN0eC5tb3ZlVG8oXG4gICAgICBzdGFydFgsXG4gICAgICBoZWlnaHQgLSAoaGVpZ2h0UmFuZ2UgKiAodmFsdWVzW3N0YXJ0SW5kZXhdIC0gbWluKSkgLyB5UmFuZ2VcbiAgICApO1xuXG4gICAgY29uc3QgbWF4X3BvaW50c190b19kaXNwbGF5ID0gd2lkdGg7XG4gICAgY29uc3QgZGkgPVxuICAgICAgaW5kZXhSYW5nZSA+IG1heF9wb2ludHNfdG9fZGlzcGxheVxuICAgICAgICA/IE1hdGguZmxvb3IoaW5kZXhSYW5nZSAvIG1heF9wb2ludHNfdG9fZGlzcGxheSlcbiAgICAgICAgOiAxO1xuXG4gICAgZm9yIChcbiAgICAgIGxldCBpID0gTWF0aC5tYXgoMCwgc3RhcnRJbmRleCAtIGRpKTtcbiAgICAgIGkgPCBNYXRoLm1pbih2YWx1ZXMubGVuZ3RoLCBlbmRJbmRleCArIDIgKiBkaSk7XG4gICAgICBpICs9IGRpXG4gICAgKSB7XG4gICAgICBjb25zdCB4ID0gKChpIC0gc3RhcnRJbmRleCkgLyBpbmRleFJhbmdlKSAqIHdpZHRoUmFuZ2UgKyBzdGFydFg7XG4gICAgICBjb25zdCB5ID0gaGVpZ2h0IC0gKGhlaWdodFJhbmdlICogKHZhbHVlc1tpXSAtIG1pbikpIC8geVJhbmdlO1xuICAgICAgY3R4LmxpbmVUbyh4LCB5KTtcbiAgICB9XG5cbiAgICBjdHguc3Ryb2tlKCk7XG4gIH1cblxuICBnZXRBbm5vdGF0aW9uc1RvRHJhdyhzdGFydFRpbWU6IG51bWJlciwgZW5kVGltZTogbnVtYmVyKSB7XG4gICAgbGV0IGFubm90YXRpb25zVG9EcmF3ID0gW107XG5cbiAgICBjb25zdCB3aWR0aCA9IHRoaXMuY2FudmFzLndpZHRoO1xuXG4gICAgY29uc3QgbGVmdE9mZnNldFBlcmNlbnRhZ2UgPSAwO1xuICAgIGNvbnN0IHJpZ2h0T2Zmc2V0UGVyY2VudGFnZSA9IDE7XG5cbiAgICBjb25zdCBmdWxsV2lkdGhSYW5nZSA9IHdpZHRoO1xuICAgIGNvbnN0IHN0YXJ0WCA9IGZ1bGxXaWR0aFJhbmdlICogbGVmdE9mZnNldFBlcmNlbnRhZ2U7XG4gICAgY29uc3QgZW5kWCA9IGZ1bGxXaWR0aFJhbmdlICogcmlnaHRPZmZzZXRQZXJjZW50YWdlO1xuICAgIGNvbnN0IHdpZHRoUmFuZ2UgPSBlbmRYIC0gc3RhcnRYO1xuICAgIGNvbnN0IHRpbWVSYW5nZSA9IGVuZFRpbWUgLSBzdGFydFRpbWU7XG5cbiAgICBmb3IgKGxldCBpID0gMDsgaSA8IHRoaXMuYW5ub3RhdGlvbnMubGVuZ3RoOyBpKyspIHtcbiAgICAgIGNvbnN0IGFubiA9IHRoaXMuYW5ub3RhdGlvbnNbaV07XG4gICAgICBpZiAoXG4gICAgICAgIChhbm4uc3RhcnQgPj0gc3RhcnRUaW1lICYmIGFubi5zdGFydCA8PSBlbmRUaW1lKSB8fFxuICAgICAgICAoYW5uLmVuZCA+PSBzdGFydFRpbWUgJiYgYW5uLmVuZCA8PSBlbmRUaW1lKSB8fFxuICAgICAgICAoYW5uLnN0YXJ0IDw9IHN0YXJ0VGltZSAmJiBhbm4uZW5kID49IGVuZFRpbWUpXG4gICAgICApIHtcbiAgICAgICAgY29uc3Qgc3RhcnQgPVxuICAgICAgICAgICh3aWR0aFJhbmdlICogKE1hdGgubWF4KGFublsnc3RhcnQnXSwgc3RhcnRUaW1lKSAtIHN0YXJ0VGltZSkpIC9cbiAgICAgICAgICB0aW1lUmFuZ2U7XG4gICAgICAgIGNvbnN0IGVuZCA9XG4gICAgICAgICAgKHdpZHRoUmFuZ2UgKiAoTWF0aC5taW4oYW5uWydlbmQnXSwgZW5kVGltZSkgLSBzdGFydFRpbWUpKSAvXG4gICAgICAgICAgdGltZVJhbmdlO1xuXG4gICAgICAgIGFubm90YXRpb25zVG9EcmF3LnB1c2goe1xuICAgICAgICAgIHN0YXJ0OiBzdGFydFggKyBzdGFydCxcbiAgICAgICAgICB3aWR0aDogZW5kIC0gc3RhcnQsXG4gICAgICAgICAgY29sb3I6ICcjNjA3RDhCJyxcbiAgICAgICAgICBpbmRleDogaSxcbiAgICAgICAgfSk7XG4gICAgICB9XG4gICAgfVxuXG4gICAgcmV0dXJuIGFubm90YXRpb25zVG9EcmF3O1xuICB9XG5cbiAgZHJhd0Fubm90YXRpb25zKHN0YXJ0VGltZTogbnVtYmVyLCBlbmRUaW1lOiBudW1iZXIpIHtcbiAgICBjb25zdCBjdHggPSB0aGlzLmNhbnZhcy5nZXRDb250ZXh0KCcyZCcpO1xuXG4gICAgaWYgKCFjdHgpIHtcbiAgICAgIGNvbnNvbGUuZXJyb3IoJ0ZhaWxlZCB0byBnZXQgMkQgY29udGV4dCcpO1xuICAgICAgcmV0dXJuO1xuICAgIH1cblxuICAgIGNvbnN0IGhlaWdodCA9IHRoaXMuY2FudmFzLmhlaWdodDtcbiAgICBjb25zdCBpbmRpY2F0b3JQYWRkaW5nID0gMTtcbiAgICBjb25zdCBpbmRpY2F0b3JIZWlnaHQgPSA1O1xuXG4gICAgY29uc3QgYW5ub3RhdGlvbnNUb0RyYXcgPSB0aGlzLmdldEFubm90YXRpb25zVG9EcmF3KHN0YXJ0VGltZSwgZW5kVGltZSk7XG5cbiAgICBmb3IgKGxldCBpID0gMDsgaSA8IGFubm90YXRpb25zVG9EcmF3Lmxlbmd0aDsgaSsrKSB7XG4gICAgICBjb25zdCBhbm4gPSBhbm5vdGF0aW9uc1RvRHJhd1tpXTtcbiAgICAgIGxldCBjb2xvciA9IGFubi5jb2xvcjtcbiAgICAgIGxldCB0cmFuc3BhcmVuY3kgPSAnMjInO1xuICAgICAgaWYgKHRoaXMuc2VsZWN0ZWRBbm5JbmRleCAhPSBudWxsKSB7XG4gICAgICAgIGNvbG9yID0gYW5uLmluZGV4ID09IHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA/IGFubi5jb2xvciA6ICcjNzg5MDlDJztcbiAgICAgICAgdHJhbnNwYXJlbmN5ID0gYW5uLmluZGV4ID09IHRoaXMuc2VsZWN0ZWRBbm5JbmRleCA/ICc0NCcgOiAnMjInO1xuICAgICAgfVxuXG4gICAgICBjdHguZmlsbFN0eWxlID0gY29sb3IgKyB0cmFuc3BhcmVuY3k7XG4gICAgICBjdHguZmlsbFJlY3QoYW5uLnN0YXJ0LCAwLCBhbm4ud2lkdGgsIGhlaWdodCk7XG5cbiAgICAgIGN0eC5maWxsU3R5bGUgPSBjb2xvcjtcbiAgICAgIGN0eC5maWxsUmVjdChcbiAgICAgICAgYW5uLnN0YXJ0ICsgaW5kaWNhdG9yUGFkZGluZyxcbiAgICAgICAgaW5kaWNhdG9yUGFkZGluZyxcbiAgICAgICAgYW5uLndpZHRoIC0gMiAqIGluZGljYXRvclBhZGRpbmcsXG4gICAgICAgIGluZGljYXRvckhlaWdodCAtIGluZGljYXRvclBhZGRpbmdcbiAgICAgICk7XG5cbiAgICAgIGlmICh0aGlzLnNlbGVjdGVkQW5uSW5kZXggPT0gYW5uLmluZGV4KSB7XG4gICAgICAgIGN0eC5saW5lQ2FwID0gJ3JvdW5kJztcbiAgICAgICAgY3R4LnN0cm9rZVN0eWxlID0gY29sb3I7XG4gICAgICAgIGN0eC5saW5lV2lkdGggPSA0O1xuXG4gICAgICAgIC8vIExlZnQgaGFuZGxlXG4gICAgICAgIGN0eC5iZWdpblBhdGgoKTtcbiAgICAgICAgY3R4Lm1vdmVUbyhhbm4uc3RhcnQgLSA0LCBoZWlnaHQgLyAyIC0gMTIpO1xuICAgICAgICBjdHgubGluZVRvKGFubi5zdGFydCAtIDQsIGhlaWdodCAvIDIgKyAxMik7XG4gICAgICAgIGN0eC5zdHJva2UoKTtcblxuICAgICAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgICAgIGN0eC5tb3ZlVG8oYW5uLnN0YXJ0ICsgNCwgaGVpZ2h0IC8gMiAtIDEyKTtcbiAgICAgICAgY3R4LmxpbmVUbyhhbm4uc3RhcnQgKyA0LCBoZWlnaHQgLyAyICsgMTIpO1xuICAgICAgICBjdHguc3Ryb2tlKCk7XG5cbiAgICAgICAgLy8gUmlnaHQgaGFuZGxlXG4gICAgICAgIGN0eC5iZWdpblBhdGgoKTtcbiAgICAgICAgY3R4Lm1vdmVUbyhhbm4uc3RhcnQgKyBhbm4ud2lkdGggLSA0LCBoZWlnaHQgLyAyIC0gMTIpO1xuICAgICAgICBjdHgubGluZVRvKGFubi5zdGFydCArIGFubi53aWR0aCAtIDQsIGhlaWdodCAvIDIgKyAxMik7XG4gICAgICAgIGN0eC5zdHJva2UoKTtcblxuICAgICAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgICAgIGN0eC5tb3ZlVG8oYW5uLnN0YXJ0ICsgYW5uLndpZHRoICsgNCwgaGVpZ2h0IC8gMiAtIDEyKTtcbiAgICAgICAgY3R4LmxpbmVUbyhhbm4uc3RhcnQgKyBhbm4ud2lkdGggKyA0LCBoZWlnaHQgLyAyICsgMTIpO1xuICAgICAgICBjdHguc3Ryb2tlKCk7XG4gICAgICB9XG4gICAgfVxuICB9XG5cbiAgY2xlYXJGcmFtZSgpIHtcbiAgICBjb25zdCBjdHggPSB0aGlzLmNhbnZhcy5nZXRDb250ZXh0KCcyZCcpO1xuICAgIGNvbnN0IHdpZHRoID0gdGhpcy5jYW52YXMud2lkdGg7XG4gICAgY29uc3QgaGVpZ2h0ID0gdGhpcy5jYW52YXMuaGVpZ2h0O1xuXG4gICAgaWYgKCFjdHgpIHtcbiAgICAgIGNvbnNvbGUuZXJyb3IoJ0ZhaWxlZCB0byBnZXQgMkQgY29udGV4dCcpO1xuICAgICAgcmV0dXJuO1xuICAgIH1cblxuICAgIGN0eC5jbGVhclJlY3QoMCwgMCwgd2lkdGgsIGhlaWdodCk7XG5cbiAgICBjdHguc3Ryb2tlU3R5bGUgPSAnIzYwN2Q4Yic7XG5cbiAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgY3R4Lm1vdmVUbygwLCBoZWlnaHQgLyAyKTtcbiAgICBjdHgubGluZVRvKHdpZHRoLCBoZWlnaHQgLyAyKTtcbiAgICBjdHguc3Ryb2tlKCk7XG5cbiAgICBjdHguYmVnaW5QYXRoKCk7XG4gICAgY3R4Lm1vdmVUbyh3aWR0aCAvIDIsIDApO1xuICAgIGN0eC5saW5lVG8od2lkdGggLyAyLCBoZWlnaHQpO1xuICAgIGN0eC5zdHJva2UoKTtcbiAgfVxuXG4gIHN5bmNUaW1lQ2hhbmdlZCgpIHtcbiAgICB0aGlzLmN1cnJlbnRUaW1lID0gdGhpcy5tb2RlbC5nZXQoJ3N5bmNfdGltZScpO1xuICB9XG5cbiAgaXNSdW5uaW5nQ2hhbmdlZCgpIHt9XG5cbiAgcmVuZGVyKCkge1xuICAgIHRoaXMubW9kZWwub24oJ2NoYW5nZTpzeW5jX3RpbWUnLCB0aGlzLnN5bmNUaW1lQ2hhbmdlZC5iaW5kKHRoaXMpKTtcbiAgICB0aGlzLm1vZGVsLm9uKCdjaGFuZ2U6aXNfcnVubmluZycsIHRoaXMuaXNSdW5uaW5nQ2hhbmdlZC5iaW5kKHRoaXMpKTtcblxuICAgIHRoaXMuc3RlcCA9IHRoaXMuc3RlcC5iaW5kKHRoaXMpO1xuICAgIHRoaXMuYW5pbWF0aW9uRnJhbWVSZXF1ZXN0SWQgPSByZXF1ZXN0QW5pbWF0aW9uRnJhbWUodGhpcy5zdGVwKTtcbiAgfVxuXG4gIGRlc3Ryb3koKSB7XG4gICAgY2FuY2VsQW5pbWF0aW9uRnJhbWUodGhpcy5hbmltYXRpb25GcmFtZVJlcXVlc3RJZCEpO1xuICB9XG59XG5cbmV4cG9ydCBkZWZhdWx0IHtcbiAgcmVuZGVyKHByb3BzOiBSZW5kZXJQcm9wczxUaW1lcnNlcmllc1dpZGdldE1vZGVsPikge1xuICAgIGNvbnN0IHdpZGdldCA9IG5ldyBUaW1lc2VyaWVzV2lkZ2V0KHByb3BzKTtcbiAgICB3aWRnZXQucmVuZGVyKCk7XG4gICAgcmV0dXJuICgpID0+IHdpZGdldC5kZXN0cm95KCk7XG4gIH0sXG59O1xuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUFBOzs7QUNtQ0EsSUFBTSxtQkFBTixNQUF1QjtBQUFBLEVBcUNyQixZQUFZLEVBQUUsT0FBTyxHQUFHLEdBQXdDO0FBMUJoRSw0QkFBdUMsQ0FBQztBQUd4Qyx1Q0FBMEQ7QUFDMUQsbUNBQXlDO0FBR3pDLGtCQUF5QixDQUFDO0FBRzFCLHVCQUE0QixDQUFDO0FBQzdCLGdCQUFpQixDQUFDO0FBRWxCLDRCQUFtQjtBQUNuQiw0QkFBa0M7QUFDbEMsa0NBR1c7QUFDWCw4QkFLVztBQUdULFNBQUssUUFBUTtBQUNiLFNBQUssS0FBSztBQUNWLE9BQUcsWUFBWTtBQUVmLFNBQUssU0FBUyxHQUFHLGNBQWMsU0FBUztBQUN4QyxTQUFLLE9BQU8saUJBQWlCLGFBQWEsS0FBSyxnQkFBZ0IsS0FBSyxJQUFJLENBQUM7QUFDekUsU0FBSyxPQUFPLGlCQUFpQixhQUFhLEtBQUssZ0JBQWdCLEtBQUssSUFBSSxDQUFDO0FBQ3pFLFNBQUssT0FBTyxp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LEVBQUU7QUFDckQsWUFBSSxPQUFPO0FBRVgsWUFBSSxVQUFVO0FBQ2QsWUFBSSxPQUFPLElBQUksUUFBUSxJQUFJLFFBQVEsR0FBRyxTQUFTLElBQUksRUFBRTtBQUNyRCxZQUFJLE9BQU8sSUFBSSxRQUFRLElBQUksUUFBUSxHQUFHLFNBQVMsSUFBSSxFQUFFO0FBQ3JELFlBQUksT0FBTztBQUFBLE1BQ2I7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBRUEsYUFBYTtBQUNYLFVBQU0sTUFBTSxLQUFLLE9BQU8sV0FBVyxJQUFJO0FBQ3ZDLFVBQU0sUUFBUSxLQUFLLE9BQU87QUFDMUIsVUFBTSxTQUFTLEtBQUssT0FBTztBQUUzQixRQUFJLENBQUMsS0FBSztBQUNSLGNBQVEsTUFBTSwwQkFBMEI7QUFDeEM7QUFBQSxJQUNGO0FBRUEsUUFBSSxVQUFVLEdBQUcsR0FBRyxPQUFPLE1BQU07QUFFakMsUUFBSSxjQUFjO0FBRWxCLFFBQUksVUFBVTtBQUNkLFFBQUksT0FBTyxHQUFHLFNBQVMsQ0FBQztBQUN4QixRQUFJLE9BQU8sT0FBTyxTQUFTLENBQUM7QUFDNUIsUUFBSSxPQUFPO0FBRVgsUUFBSSxVQUFVO0FBQ2QsUUFBSSxPQUFPLFFBQVEsR0FBRyxDQUFDO0FBQ3ZCLFFBQUksT0FBTyxRQUFRLEdBQUcsTUFBTTtBQUM1QixRQUFJLE9BQU87QUFBQSxFQUNiO0FBQUEsRUFFQSxrQkFBa0I7QUFDaEIsU0FBSyxjQUFjLEtBQUssTUFBTSxJQUFJLFdBQVc7QUFBQSxFQUMvQztBQUFBLEVBRUEsbUJBQW1CO0FBQUEsRUFBQztBQUFBLEVBRXBCLFNBQVM7QUFDUCxTQUFLLE1BQU0sR0FBRyxvQkFBb0IsS0FBSyxnQkFBZ0IsS0FBSyxJQUFJLENBQUM7QUFDakUsU0FBSyxNQUFNLEdBQUcscUJBQXFCLEtBQUssaUJBQWlCLEtBQUssSUFBSSxDQUFDO0FBRW5FLFNBQUssT0FBTyxLQUFLLEtBQUssS0FBSyxJQUFJO0FBQy9CLFNBQUssMEJBQTBCLHNCQUFzQixLQUFLLElBQUk7QUFBQSxFQUNoRTtBQUFBLEVBRUEsVUFBVTtBQUNSLHlCQUFxQixLQUFLLHVCQUF3QjtBQUFBLEVBQ3BEO0FBQ0Y7QUFFQSxJQUFPQSw2QkFBUTtBQUFBLEVBQ2IsT0FBTyxPQUE0QztBQUNqRCxVQUFNLFNBQVMsSUFBSSxpQkFBaUIsS0FBSztBQUN6QyxXQUFPLE9BQU87QUFDZCxXQUFPLE1BQU0sT0FBTyxRQUFRO0FBQUEsRUFDOUI7QUFDRjsiLAogICJuYW1lcyI6IFsidGltZXNlcmllc193aWRnZXRfZGVmYXVsdCJdCn0K
