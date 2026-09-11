# HomeOps Agent Demo Video Script

Target length: 3 to 4 minutes.

## 0:00-0:25 Problem

Smart homes are helpful, but mine is not one clean system. It is Echo devices, outlets, lights, TV, Alexa routines, and a front door lock that should never be treated casually. The friction is not turning one thing on or off. The friction is checking the whole state of the home and knowing what should happen next.

## 0:25-0:50 Thesis

HomeOps Agent is not a smart-home remote. It is an operations layer for the home. It checks what is true now, handles low-risk routine actions, and stops when a decision needs human judgment.

## 0:50-1:45 Working Demo

In the demo, I run a Good Night Check across simulated devices: a front door lock, Govee bedside bulb, SwitchBot outlet, Fire TV, and Echo surround group.

When the outlet is on, the agent turns it off. When the light is too bright, it dims it. When Fire TV is active, it confirms the media state. These are low-risk routine actions.

The page also shows the tool trace, so you can see the agent loop: get device state, execute safe action, request approval when needed, and write to the audit log.

## 1:45-2:35 Safety Scenario

The important part is what the agent refuses to do. When the front door lock status is unknown, it does not guess. It does not unlock anything. It creates a human approval request and records that decision in the audit trail.

That is the product judgment behind this project. The goal is not more automation for its own sake. The goal is less repetitive checking and a clearer boundary around consequential decisions.

## 2:35-3:15 Technical Implementation

The project uses Python and the Strands Agents SDK. The HomeOps tools are explicit: get device state, execute safe actions, request human approval, and write the audit log. The web demo uses deterministic simulation so the workflow is reliable for judging, and the Strands adapter is wired with the official Agent and tool interfaces for model-backed execution.

## 3:15-3:45 Impact

This could grow into a practical assistant for households, caregivers, property managers, or anyone coordinating a mix of smart-home devices. It is useful because it respects the messy reality of home systems while keeping humans in control.

## Closing

HomeOps Agent makes the smart home feel less like a pile of commands and more like a system you can trust.
