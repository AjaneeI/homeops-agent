# Devpost Copy Draft

## Project Name

HomeOps Agent

## Short Description

HomeOps Agent coordinates a mixed smart home by checking device state, completing low-risk routine actions, and escalating safety-sensitive decisions to the human.

## Inspiration

Smart homes are useful, but they can become fragmented across routines, apps, devices, and voice commands. HomeOps Agent explores what happens when the home has an operations layer: one agent that checks the current state, handles routine fixes, and keeps people in control of consequential decisions.

## What It Does

The MVP runs a Good Night Check across simulated smart-home devices: a front door lock, Govee bedside bulb, SwitchBot outlet, Fire TV, and Echo surround group. It dims lights, turns off low-risk outlets, confirms media devices are idle, and pauses on lock uncertainty instead of acting automatically.

## Safety

HomeOps Agent is intentionally conservative. It never unlocks doors automatically, never changes access automatically, and records every action in an audit trail. The point is not to remove human judgment. It is to reduce repetitive checking while surfacing the moments that actually need attention.

## Built With

Python, JavaScript, HTML, CSS, simulated device tools, and a Strands-ready agent/tool architecture. Final submission will wire the existing adapter to the Strands Agents SDK.

## Testing Instructions

1. Run `python3 -m http.server 4173 -d web`.
2. Open `http://localhost:4173`.
3. Select each demo scenario.
4. Click `Run Good Night Check`.
5. Confirm that safe actions run automatically and lock uncertainty creates an approval request.
