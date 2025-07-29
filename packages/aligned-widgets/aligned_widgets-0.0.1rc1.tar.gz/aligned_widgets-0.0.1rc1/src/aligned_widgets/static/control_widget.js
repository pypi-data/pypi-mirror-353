var a=`<div class="widget control-widget">
  <div class="control-buttons">
    <button id="btn-toggle-play"></button>
  </div>
  <div class="progress-slider">
    <input
      type="range"
      min="0"
      max="1"
      value="0"
      step="0.01"
      class="slider"
      id="input-range-progress"
    />
  </div>
  <div class="time-display">
    <span id="span-current-time" class="time">00:00</span>
    <span class="seperator">/</span>
    <span id="span-total-time" class="time">00:00</span>
  </div>
</div>
`;var n=class{constructor({model:t,el:e}){this.lastAnimationFrameTimestamp=null;this.animationFrameRequestId=null;this.model=t,this.el=e,this.currentTime=this.model.get("sync_time"),this.el.innerHTML=a,this.btnTogglePlay=e.querySelector("#btn-toggle-play"),this.inputRangeProgress=e.querySelector("#input-range-progress"),this.spanCurrentTime=e.querySelector("#span-current-time"),this.spanTotalTime=e.querySelector("#span-total-time"),this.btnTogglePlay.innerHTML=this.model.get("icons").play,this.spanTotalTime.innerHTML=this.formatTime(this.model.get("duration")),this.btnTogglePlay.addEventListener("click",this.btnTogglePlayClicked.bind(this)),this.inputRangeProgress.addEventListener("change",this.inputRangeProgressChanged.bind(this))}inputRangeProgressChanged(t){let e=+t.target.value;this.currentTime=e*this.model.get("duration"),this.model.set("sync_time",this.currentTime),this.model.save_changes()}btnTogglePlayClicked(){this.model.set("sync_time",this.currentTime),this.model.set("is_running",!this.model.get("is_running")),this.model.save_changes()}step(t){this.lastAnimationFrameTimestamp||(this.lastAnimationFrameTimestamp=t);let e=t-this.lastAnimationFrameTimestamp;if(this.lastAnimationFrameTimestamp=t,this.model.get("is_running")){let i=this.model.get("duration");this.currentTime=Math.min(this.currentTime+e/1e3,i),this.inputRangeProgress.value=(this.currentTime/i).toFixed(2),this.spanCurrentTime.innerHTML=this.formatTime(this.currentTime)}this.animationFrameRequestId=requestAnimationFrame(this.step)}syncTimeChanged(){this.currentTime=this.model.get("sync_time"),this.inputRangeProgress.value=(this.currentTime/this.model.get("duration")).toFixed(2)}isRunningChanged(){this.btnTogglePlay.innerHTML=this.model.get("is_running")?this.model.get("icons").pause:this.model.get("icons").play}formatTime(t){let e=Math.floor(t/3600),i=Math.floor(t%3600/60),l=Math.floor(t%60),r=String(i).padStart(2,"0"),o=String(l).padStart(2,"0");return e>0?`${String(e).padStart(2,"0")}:${r}:${o}`:`${r}:${o}`}render(){this.model.on("change:sync_time",this.syncTimeChanged.bind(this)),this.model.on("change:is_running",this.isRunningChanged.bind(this)),this.step=this.step.bind(this),this.animationFrameRequestId=requestAnimationFrame(this.step)}destroy(){cancelAnimationFrame(this.animationFrameRequestId)}},y={render(s){let t=new n(s);return t.render(),()=>t.destroy()}};export{y as default};
