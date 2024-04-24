import { expect } from "chai";

import { videoTimeString } from "./video-util";

describe("videoTimeString", function () {
  for (const [input, expected] of [
    [0.0, "0:00.00"],
    [60.0, "1:00.00"],
    [60.15, "1:00.15"],
    [63.1, "1:03.10"],
    [60 - 1 / 29.97, "0:59.97"],
    [59.999, "1:00.00"],
    [59.994, "0:59.99"],
    [601.0, "10:01.00"],
  ]) {
    it(`returns ${expected} for ${input}`, function () {
      expect(videoTimeString(input)).to.eql(expected);
    });
  }
});
