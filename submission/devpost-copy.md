# Devpost Copy Draft

## Project Name

HomeOps Agent

## Repository

https://github.com/AjaneeI/homeops-agent

## Short Description

HomeOps Agent is an operations layer for a mixed smart home: it checks device state, completes low-risk routine actions, and escalates safety-sensitive decisions to the human.

## Inspiration

Smart homes are useful, but they can become fragmented across routines, apps, devices, and voice commands. HomeOps Agent explores what happens when the home has an operations layer instead of another remote: one agent that checks the current state, handles routine fixes, and keeps people in control of consequential decisions.

## What It Does

The MVP runs a Good Night Check across simulated smart-home devices: a front door lock, Govee bedside bulb, SwitchBot outlet, Fire TV, and Echo surround group. It dims lights, turns off low-risk outlets, confirms media devices are idle, and pauses on lock uncertainty instead of acting automatically.

The dashboard shows device state, actions taken, approval requests, audit history, and a visible tool-call trace so the agent workflow is easy to inspect.

## Safety

HomeOps Agent is intentionally conservative. It never unlocks doors automatically, never changes access automatically, and records every action in an audit trail. The point is not to remove human judgment. It is to reduce repetitive checking while surfacing the moments that actually need attention.

## Built With

Python, JavaScript, HTML, CSS, simulated device tools, and the Strands Agents SDK using the official `Agent` and `@tool` interfaces.

## Testing Instructions

1. Run `python3 -m http.server 4173 -d web`.
2. Open `http://localhost:4173`.
3. Select each demo scenario.
4. Click `Run Good Night Check`.
5. Confirm that safe actions run automatically, lock uncertainty creates an approval request, and the tool trace records the agent loop.
