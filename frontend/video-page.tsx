// Note: there’s no typescript dependency in package.json, or tsconfig.json yet
import { createRoot } from "react-dom/client";
import React, { MutableRefObject, useEffect, useRef, useState } from "react";
import { runOnLoad } from "./util";
import * as classNames from "classnames";
import { videoTimeString } from "./video-util";
import { uint8ArrayToBase64 } from "uint8array-extras";
import Cookies from "js-cookie";

type Nullable<T> = T | null;

const FRAME_RATE = 29.97;

// The `active` parameter is so that we’re still calling useEffect even if the
// hook isn’t needed.
function keyEffect(
  {
    key,
    callback,
    active,
    allowRepeat = false,
    evenIfElementFocused = false,
    meta = undefined,
  },
  deps = []
) {
  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if (
        event.key == key &&
        // when focused on a non-body element like a textbox, skip handling
        // everything except Escape
        (evenIfElementFocused ||
          event.target == document.body ||
          event.target != document.activeElement ||
          document.activeElement.tagName.toLowerCase() == "video") &&
        (allowRepeat || !event.repeat) &&
        !event.isComposing &&
        !event.altKey &&
        !event.ctrlKey &&
        ((!meta && !event.metaKey) || (meta && event.metaKey))
      ) {
        event.stopPropagation();
        event.preventDefault();
        callback();
      }
    };

    if (active) {
      document.addEventListener("keydown", listener);
      return () => {
        document.removeEventListener("keydown", listener);
      };
    }
  }, [active, ...deps]);
}

function toggleFullScreen(element: Nullable<HTMLElement>) {
  if (document.fullscreenElement) {
    document.exitFullscreen();
    return;
  }

  if (!element) {
    return;
  }

  element.requestFullscreen();
}

function togglePlayPause(video?: HTMLVideoElement | null) {
  if (!video) {
    return;
  }

  if (video.paused) {
    video.play();
  } else {
    video.pause();
  }
}

// Skip video playback forward or backward by `time` seconds. Negative numbers
// go backwards.
function skip(
  video: Nullable<HTMLVideoElement>,
  time: number,
  options: { pause: boolean } = { pause: false }
) {
  if (!video) {
    return;
  }

  if (!video.duration) {
    return;
  }

  if (options.pause) {
    if (!video.paused) {
      video.pause();
    }
  }

  let newTime = video.currentTime + time;
  newTime = Math.max(0, newTime);
  newTime = Math.min(newTime, video.duration);
  video.currentTime = newTime;
}

function toggleSubtitles(video: Nullable<HTMLVideoElement>) {
  const trackList = video?.textTracks;
  if (trackList.length < 0) {
    return;
  }

  const track = trackList[0];
  if (track.mode == "showing") {
    track.mode = "hidden";
  } else {
    track.mode = "showing";
  }
}

function NoteModal({
  videoRef,
  setTakingNote,
  seriesSlug,
  episodeSlug,
}: {
  videoRef: MutableRefObject<HTMLVideoElement>;
  setTakingNote: (boolean) => void;
  seriesSlug: string;
  episodeSlug: string;
}) {
  const textRef = useRef(null);

  useEffect(() => {
    textRef?.current.focus();
  });

  const [captureBlob, setCaptureBlob] = useState(null);

  if (!captureBlob) {
    previewBlob(videoRef.current).then((b) => {
      if (b) setCaptureBlob(b);
    });
  }

  keyEffect({
    key: "Escape",
    callback: () => setTakingNote(false),
    active: true,
    evenIfElementFocused: true,
  });
  keyEffect({
    key: "F1",
    callback: () => setTakingNote(false),
    active: true,
    evenIfElementFocused: true,
  });
  keyEffect(
    {
      key: "Enter",
      callback: () =>
        saveModal({
          textRef,
          videoRef,
          setTakingNote,
          seriesSlug,
          episodeSlug,
          captureBlob,
        }),
      active: true,
      evenIfElementFocused: true,
      meta: true,
    },
    [captureBlob]
  );

  return (
    <>
      <div className="note-modal-overlay"></div>
      <div className="note-modal">
        <h1>Add note at {videoTimeString(videoRef?.current?.currentTime)}</h1>
        <div className="note-modal-contents-wrapper">
          {captureBlob && (
            <img
              className="note-modal-image-preview"
              src={URL.createObjectURL(captureBlob)}
            />
          )}
          <textarea
            placeholder="note…"
            className="note-modal-textarea"
            ref={textRef}
          />
        </div>
        <button
          onClick={() =>
            saveModal({
              textRef,
              videoRef,
              setTakingNote,
              seriesSlug,
              episodeSlug,
              captureBlob,
            })
          }
        >
          Save (⌘↩)
        </button>
      </div>
    </>
  );
}

async function previewBlob(video) {
  if (!video) {
    return;
  }

  console.log("computing preview");

  const canvas = new OffscreenCanvas(video.clientWidth, video.clientHeight);

  // Assuming no vertical letterboxing
  const scale = video.videoHeight / video.clientHeight;
  const scaledWidth = video.videoWidth / scale;
  const overflow = scaledWidth - canvas.width;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(
    video,
    0,
    0,
    video.videoWidth,
    video.videoHeight,
    -overflow / 2,
    0,
    video.videoWidth / scale,
    video.videoHeight / scale
  );

  return canvas.convertToBlob({ type: "image/jpeg", quality: 0.5 });
}

async function saveModal({
  videoRef,
  textRef,
  setTakingNote,
  seriesSlug,
  episodeSlug,
  captureBlob,
}: {
  videoRef: MutableRefObject<HTMLVideoElement>;
  textRef: MutableRefObject<HTMLTextAreaElement>;
  setTakingNote;
  seriesSlug: string;
  episodeSlug: string;
  captureBlob: Blob;
}) {
  const noteText = textRef.current.value;
  const video = videoRef.current;

  const position = videoTimeString(video.currentTime);

  const base64image = uint8ArrayToBase64(
    new Uint8Array(await captureBlob.arrayBuffer())
  );

  const payload = {
    seriesSlug,
    episodeSlug,
    videoPosition: position,
    text: noteText,
    image: base64image,
    imageType: captureBlob.type,
  };

  const response = await fetch("/vid0/savenote", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": Cookies.get("csrftoken"),
    },
    mode: "same-origin",
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    console.log(await response.json());

    setTakingNote(false);
  } else {
    console.error("failed to save note", response.status, response.statusText);
  }
}

function VideoPlayer({ seriesSlug, episodeSlug }) {
  const videoElementRef: MutableRefObject<HTMLVideoElement> = useRef(null);
  const playerDivRef = useRef(null);

  const [cropped, setCropped] = useState(false);
  const [takingNote, setTakingNote] = useState(false);

  const active = !takingNote;
  keyEffect({
    key: "n",
    callback: () => {
      const video = videoElementRef?.current;
      if (!video) {
        return;
      }

      video.pause();
      setTakingNote(true);
    },
    active,
  });

  keyEffect({
    key: "f",
    callback: () => toggleFullScreen(playerDivRef?.current),
    active,
  });
  keyEffect(
    {
      key: "c",
      callback: () => setCropped(!cropped),
      active,
    },
    [cropped]
  );

  keyEffect({
    key: " ",
    callback: () => togglePlayPause(videoElementRef?.current),
    active,
  });
  keyEffect({
    key: "ArrowLeft",
    callback: () => skip(videoElementRef?.current, -5),
    active,
    allowRepeat: true,
  });
  keyEffect({
    key: "ArrowRight",
    callback: () => skip(videoElementRef?.current, 5),
    active,
    allowRepeat: true,
  });
  keyEffect({
    key: "j",
    callback: () => {
      skip(videoElementRef?.current, -1 / FRAME_RATE, { pause: true });
    },
    active,
    allowRepeat: true,
  });
  keyEffect({
    key: "k",
    callback: () =>
      skip(videoElementRef?.current, 1 / FRAME_RATE, { pause: true }),
    active,
    allowRepeat: true,
  });
  keyEffect({
    key: "s",
    callback: () => toggleSubtitles(videoElementRef?.current),
    active,
  });

  return (
    <div className="video-player" ref={playerDivRef}>
      {takingNote && (
        <NoteModal
          setTakingNote={setTakingNote}
          videoRef={videoElementRef}
          seriesSlug={seriesSlug}
          episodeSlug={episodeSlug}
        />
      )}
      <video
        controls
        src={`/vid0/mp4/${seriesSlug}/${episodeSlug}`}
        ref={videoElementRef}
        className={classNames({ cropped43: cropped })}
      >
        <track
          kind="subtitles"
          label="English"
          srcLang="en"
          src={`/vid0/vtt/${seriesSlug}/${episodeSlug}`}
        />
      </video>
    </div>
  );
}

runOnLoad(() => {
  const element = document.getElementById("video1");
  const root = createRoot(element);
  root.render(
    <VideoPlayer
      seriesSlug={element.dataset["seriesslug"]}
      episodeSlug={element.dataset["episodeslug"]}
    />
  );
});
