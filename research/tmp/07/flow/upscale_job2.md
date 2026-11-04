# Flow 1080p upscale (`upscale_061235_1080.mp4`) = job2: verdict

Numbers: `upscale_job2.txt` (script `upscale.py`). Crops at 100 %: `tmp/07/tablero/flow_upscale_job2.jpg`. At speed,
100 % crops, plaster 0–39 and stone 150–191: `tmp/07/tablero/flow_upscale_job2_textura.mp4` (left 720p+lanczos,
right upscale).

- **Which job:** job2. Reduced to 720p it differs from job2 by a mean of 1.37 (max 1.79); from job1 by 24.6.
- **Ends:** unchanged in geometry. Frame 0 against start.png and frame 184 against end.png are offset by 0.0–0.1 px.
  But the pixel difference to the plates grows (frame 0: 6.3 against 4.5 for 720p+lanczos; frame 184: 4.5 against
  3.1) because the added detail is not the plate's.
- **Colour and light:** unchanged; the mean is under 1 level per channel (worst frame −0.95).
- **Oversharpening:** yes. Laplacian variance at 2.3–2.5× **the plate's** (plaster 1098 against 470, guitar 626
  against 257, telephone 1669 against 668, stone 447 against 194), while 720p+lanczos sits at 0.4×. In the crops, the
  plaster gets etched relief and cracks the plate doesn't have, the tezontle stone turns crunchy, and the telephone's
  edges show a sharpening halo with the dial redrawn.
- **Texture crawl / flicker:** yes, moderate. The high-frequency energy of the frame-to-frame difference is 1.8× that
  of 720p+lanczos (stone nearly still 168–191: 3.50 against 1.90; camarín 0–12: 9.10 against 5.34).

**Verdict:** the upscale moves nothing and changes no light, but it invents texture that is sharper than the plates
and crawls. At the join with the E5 loops (made from the plates), there would be a visible jump in texture at
frames 0 and 184. If job2 is used as the temporary E6: ~8–12 frames of cross-fade to the plate at each end, or soften
the upscale toward the plates' sharpness (a mix with 720p+lanczos lands in between). Not tested.
