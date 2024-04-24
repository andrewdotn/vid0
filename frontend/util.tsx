export function runOnLoad(func) {
  // https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event#checking_whether_loading_is_already_complete
  if (document.readyState == "loading") {
    document.addEventListener("DOMContentLoaded", (e) => func());
  } else {
    func();
  }
}
