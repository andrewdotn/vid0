export function videoTimeString(time) {
  time = Math.round(time * 100) / 100;

  const minutes = Math.floor(time / 60);
  const minuteString = minutes.toString();

  time -= minutes * 60;

  const seconds = Math.trunc(time);
  const secondString = seconds.toString().padStart(2, "0");

  time -= seconds;
  const fraction = time;
  const fractionString = Math.round(100 * fraction)
    .toString()
    .padEnd(2, "0");

  return `${minuteString}:${secondString}.${fractionString}`;
}
