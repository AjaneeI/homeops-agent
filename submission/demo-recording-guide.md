# HomeOps Agent Demo Recording Guide

Target length: 2 to 3 minutes. Keep it public, under the hackathon's 5-minute limit.

## Recommended Flow

1. Open the hosted demo: https://homeops-agent.ajaneeigharo.chatgpt.site
2. Start screen recording with the browser window centered.
3. Show the top thesis: "Not a remote. An operations layer for the home."
4. Run the default "Outlet/light fix needed" scenario.
5. Pause briefly on the device state, actions taken, tool trace, and audit trail.
6. Switch to "Lock status unknown."
7. Run the check again and pause on the approval request.
8. Switch to "Device API failure."
9. Run the check again and show that the failed light action is reported while the device is left unchanged.
10. End on the safety point: the agent handles routine work, but it does not guess on locks, access, or broken device state.

## Judge-Facing Story Beats

Use these moments as anchors while recording:

1. Product thesis: this is an operations layer, not another control panel.
2. Technical proof: the tool trace makes the Strands-style loop visible.
3. Safety proof: lock uncertainty creates approval instead of automatic action.
4. Reliability proof: device failure is recorded and does not silently change state.
5. Growth path: AgentCore can host the Strands agent while tool boundaries stay stable.

## Voiceover Direction

Use the narration in `submission/demo-narration.txt`.

The best voice style is calm, warm, and precise. It should sound like a capable builder explaining product judgment, not a hype video.

Suggested AI voice settings:

- Gender/presentation: neutral or lightly feminine
- Pace: medium
- Tone: composed, practical, confident
- Emotion: low-drama, warm, clear
- Avoid: salesy, breathless, influencer-style, overly cinematic

## Fast Production Options

- Descript, ElevenLabs, CapCut, or Canva can generate natural narration from the script.
- If using CapCut or Canva, record the screen first, import it, then paste the narration into text-to-speech.
- If using Descript or ElevenLabs, export the narration as MP3 or WAV, then place it over the screen recording.

## Upload Checklist

- Video is public or unlisted on YouTube/Vimeo.
- Length is under 5 minutes.
- The hosted demo URL appears in the description.
- The GitHub repo URL appears in the description.
- The safety behavior is visible, not just mentioned.
- The tool trace is visible long enough for judges to understand the Strands-style workflow.
