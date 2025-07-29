var t=`<div class="widget video-widget">
  <video id="video">
    <source src="" type="video/mp4" id="mp4-source" />
    Your browser does not support video
  </video>
</div>
`;var i=class{constructor({model:s,el:e}){this.model=s,this.el=e,this.el.innerHTML=t,this.video=e.querySelector("#video"),this.source=e.querySelector("#mp4-source"),this.source.src=this.model.get("video_url"),this.video.addEventListener("seeked",this.seeked.bind(this)),this.video.addEventListener("play",this.played.bind(this)),this.video.addEventListener("pause",this.paused.bind(this))}played(){this.model.set("is_running",!0),this.model.set("sync_time",this.video.currentTime),this.model.save_changes()}paused(){this.model.set("is_running",!1),this.model.set("sync_time",this.video.currentTime),this.model.save_changes()}seeked(){}syncTimeChanged(){console.log("syncTimeChanged",this.model.get("sync_time")),this.video.currentTime=this.model.get("sync_time")}isRunningChanged(){this.model.get("is_running")?this.video.play():this.video.pause()}render(){this.model.on("change:sync_time",this.syncTimeChanged.bind(this)),this.model.on("change:is_running",this.isRunningChanged.bind(this))}},u={render(d){new i(d).render()}};export{u as default};
