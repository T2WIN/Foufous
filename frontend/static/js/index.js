const API_URL = "http://127.0.0.1:8000/";
const MAX_ITERATIONS = 600;
const POPUP_DURATION = 2000;
var index = 0;
var queue = [];
var nextEvent = null;

function changeName(that) {
  document.getElementById("filename").innerHTML = that.files[0].name; 
}

async function mySubmitFunction(event) {
  event.preventDefault();

  const video = document.getElementById("result_video")
  if(video.src !== null)
    video.pause()

  const form = document.getElementById("myForm");
  const fd = new FormData(form);
  const loader = document.getElementById("spinner");

  // Create a 3-frame looping animation with a 2-second duration
  loader.style.display = "flex"
  createLoopingFrame(3, 2000, updateAnimation);


  const send = await fetch(API_URL + "new_task", {
    method: "POST",
    body: fd,
    cors: "Access-Control-Allow-Origin",
  });

    
  const task = await send.json();
  console.log(task.uid);
  //long polling
  const response = await long_polling(await fetch(API_URL + `task/${task.uid}`, {
    method: "GET",
  }), task.uid);

  let data = null;
  console.log(response);
  if( response.status === "complete") {
    loader.style.display = "none";
    document.getElementById("end").style.display = "flex";
    data = response.result;
    document.getElementById("result").style.display = "flex";
    video.src = URL.createObjectURL(fd.get("pitch"));
    video.play();
    window.scrollTo(0,0);
    window.scrollTo(0,video.getBoundingClientRect().y - 100);
    processGlobal(data.global);
    preprocessVideo(data.events);
  }

  return false;
}

async function preprocessVideo(events) {
  index = 0;
  queue = [];
  for(let i in  events) {
    queue.push(events[i]);
  }
  document.getElementById("events").innerHTML = "";
  processVideo();
}

async function processVideo() {
  let popup = [];
  nextEvent = queue[index] ?? null;
  const video = document.getElementById("result_video");
  let iteration = 0;
  while(nextEvent!= null  && !video.ended  && ++iteration < MAX_ITERATIONS) {
    await new Promise(r => setTimeout(r, 250));
    while (nextEvent!= null && nextEvent.timestamp - video.currentTime < 0.5) {
      // TODO : show event on video screen
      // get x and y of video
      
      const videoRect = video.getBoundingClientRect();
      
      const x = videoRect.x + 15 //(videoRect.width * nextEvent.x  ?? 1) + 1000;
      const y = videoRect.y + 15 + window.scrollY //videoRect.height * nextEvent.y ?? 1 + 100;
      const div = document.createElement("div");
      const p = document.createElement("p");

      /* add text to div */
      p.textContent = nextEvent.type;
      

      // add class to div 
      div.classList.add("pop-up")
      div.style.left = x + "px";
      div.style.top = y + popup.length * 65 + "px";

      /* add color to div */
      div.style.backgroundColor = (nextEvent.note === "good") ? "#a6d189" : (nextEvent.note === "ok" ) ? "#e5c890" : "#e78284";
      
      div.append(p);
      document.getElementById("result").appendChild(div);
      popup.push(div)

      /* show event in the list */
      const entry = document.createElement("p");
      const span = document.createElement("span");
      span.classList.add("timestamp");
      span.setAttribute("onclick", `spanClick(${nextEvent.timestamp} - 1, ${index})`);

      /* add text to span & entry */
      span.textContent =  nextEvent.timestamp.toFixed(2);
      entry.appendChild(span);
      const span2 = document.createElement("span");
      span2.classList.add(nextEvent.note === "good" ? "good" : nextEvent.note === "ok" ? "ok" : "bad");
      span2.textContent = nextEvent.type;
      entry.innerHTML += ": ";
      entry.appendChild(span2);
      document.getElementById("events").appendChild(entry);

      setTimeout(() => {
        popup.shift().remove();
        for(const child of popup) {
          child.style.top = child.getBoundingClientRect().y - 65 + window.scrollY + "px";
        }
      }, POPUP_DURATION);
      
      if(index < queue.length)
        nextEvent = queue[++index] ?? null;
      else
        nextEvent = null;
    
    }
    
  }
  
}

function processGlobal(global) {
  const globalDiv = document.getElementById("global");
  globalDiv.innerHTML = "";
  
  for(let i in global) {
    // create ul
    const li = document.createElement("li");
    const p = document.createElement("p");
    p.innerHTML = i + ": " + global[i];
    li.appendChild(p);
    globalDiv.appendChild(li);

  }
}

function spanClick(time, index_) {
  const video = document.getElementById("result_video");
  video.currentTime = time;
  index = index_
  nextEvent = queue[index];
  document.getElementById("events").innerHTML = "";

  /* very disgusting code bassed on copy and paste of preview code but We got no time */
  for(let i = 0; i < index; i++) {
    const pop = queue[i];
  /* show event in the list */
  const entry = document.createElement("p");
  const span = document.createElement("span");
  span.classList.add("timestamp");
  span.setAttribute("onclick", `spanClick(${pop.timestamp}, ${i})`);

  /* add text to span & entry */
  span.textContent = pop.timestamp.toFixed(2);
  entry.appendChild(span);
  const span2 = document.createElement("span");
  span2.classList.add(pop.note === "good" ? "good" : nextEvent.note === "ok" ? "ok" : "bad");
  span2.textContent = pop.type;
  entry.innerHTML += ": ";
  entry.appendChild(span2);
  
  document.getElementById("events").appendChild(entry); 
  }

  if(video.ended || video.paused) {
    video.play();
    processVideo();
  }
}


/* ------------------------------ */

// Function to create a looping animation frame
function createLoopingFrame(frameCount, duration, frameCallback) {
  const interval = duration / frameCount;
  let currentFrame = 0;

  setInterval(() => {
    const frame = currentFrame % frameCount;
    frameCallback(frame);
    currentFrame++;
  }, interval);
}

// Update the animation based on the current frame
function updateAnimation(frame) {
  const balls = document.querySelectorAll(".ball");
  balls.forEach((ball, index) => {
    const translateY = frame === index ? -20 : 0;
    ball.style.transform = `translateY(${translateY}px)`;
  });
}

async function long_polling(response, id) {
  const json = await response.json();
  console.log(json);
  console.log(id);
  if(json.status === "in_progress") {
  
    console.log("timeout");
    await new Promise(r => setTimeout(r, 3000));
    return long_polling(await fetch(API_URL + `task/${id}`, {
      method: "GET",
    }), id);
  }
  else if(json.status === "complete") {
    console.log("ok");
    console.log(json);
    return json;
  }
}