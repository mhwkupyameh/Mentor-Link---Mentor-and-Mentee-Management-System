# MentorLink — Mentor & Mentee Management System

> A full-featured platform to manage mentorship programs — pair mentors with mentees, schedule sessions, track goals, and measure outcomes.


<img width="1918" height="1022" alt="Screenshot 2026-05-11 142657" src="https://github.com/user-attachments/assets/b1e9dccc-984e-4396-8d81-121ad8b6bab5" />


---

## Description

**MentorLink** is a desktop-based Mentor & Mentee Management System designed to bring structure, transparency, and measurable outcomes to institutional mentorship programs. Built for organizations like **SVKM's Student Business Mentoring Program (SBMP)**, MentorLink replaces scattered spreadsheets and manual tracking with a single, cohesive platform that coordinators, mentors, and mentees can rely on.

At its core, MentorLink solves a problem that every growing mentorship program faces — the complexity of managing people, pairings, schedules, and progress all at once. The application provides a **centralized dashboard** that surfaces the metrics that matter most: total mentors and mentees, active pairs, upcoming sessions, and overall goal completion rates — all in real time.

The **Mentors and Mentees modules** allow coordinators to maintain rich, searchable profiles for every participant. Each profile captures expertise, availability, field of interest, contact details, and personal development notes, making it easy to understand who's in the program and what they bring to the table.

The **Sessions module** handles the full lifecycle of a mentoring session — from scheduling to completion. Sessions can be held online (via Google Meet or Microsoft Teams) or in person, and are tracked with statuses like Upcoming, Completed, Rescheduled, or Cancelled, ensuring nothing slips through the cracks.

The **Goals & Progress module** introduces accountability into the mentoring relationship. Coordinators and mentors can set SMART goals with due dates, categories, and priority levels. A visual progress tracker shows completion rates at both individual and program levels.

Perhaps the most powerful feature is the **Matching System** — an auto-match engine that intelligently pairs unmatched mentees with available mentors based on field alignment, with the option to create custom pairs manually.

MentorLink is built with a clean, dark-themed UI that makes navigation intuitive and data easy to read, making mentorship management feel less like administrative overhead and more like meaningful program leadership.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Data & Modules](#data--modules)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**MentorLink** is a desktop application built for institutions and organizations running structured mentorship programs. It provides coordinators with a centralized dashboard to manage mentors, mentees, pairings, sessions, and goals — all from a single, intuitive interface.

Developed as part of **SVKM's SBMP (Student Business Mentoring Program)**, MentorLink brings structure, visibility, and accountability to the mentoring process.

---

## Features

### 🏠 Dashboard
- Summary stats: total mentors, mentees, sessions, goals, and active pairs
- Goals overview with donut chart (completion %)
- People by field breakdown (mentors + mentees)
- Recent activity feed
- Goal progress by priority (High / Medium / Low)
- Quick actions: Add Mentor, Add Mentee

### 👩‍🏫 Mentors
- Add, edit, and delete mentor profiles
- Fields: name, expertise/topics, gender, age group, field, email, phone, location, experience, institution, availability (hrs/week), remarks
- Search and filter by field
- Export to CSV

### 🎓 Mentees
- Add, edit, and delete mentee profiles
- Fields: name, learning goal, gender, age group, field, email, phone, location, occupation, institution, availability, personal notes
- Search and filter by field
- Export to CSV

### 📅 Sessions
- Schedule, edit, and delete mentoring sessions
- Fields: title, mentor, mentee, date, time, duration, mode (Online — Teams / Google Meet / In-person), topic
- Status tracking: Upcoming, Completed, Rescheduled, Cancelled
- Filter by status
- Export to CSV

### 🎯 Goals & Progress
- Add SMART goals linked to a mentor-mentee pair
- Fields: goal title, mentee, mentor, due date, category (Career Growth / Academic / Portfolio / Projects), priority (High / Medium / Low)
- Status: Completed / In Progress
- Overall progress bar with completion percentage
- Filter by status and priority
- Export to CSV

### 🤝 Matching System
- Auto-match All: automatically pairs unmatched mentees with available mentors in the same field
- Manually create custom pairs via "+ Create Pair"
- View all active pairs with match date and field
- Remove pairs as needed

---

## Screenshots

| Screen | Description |
|--------|-------------|
| Dashboard | Overview of all key metrics and recent activity |
| Mentors | Full mentor roster with profile cards |
| Mentees | Full mentee roster with profile cards |
| Sessions | Chronological session list with status badges |
| Goals & Progress | Goal tracker with priority labels and completion status |
| Matching System | Auto-matched and manually created mentor-mentee pairs |

<img width="1918" height="1022" alt="Screenshot 2026-05-11 142657" src="https://github.com/user-attachments/assets/f762ab43-259d-4494-815e-32cad918f73a" />
<img width="1918" height="1017" alt="Screenshot 2026-05-11 142722" src="https://github.com/user-attachments/assets/d3cedf00-6074-411c-a7a5-2b64d29ca678" />
<img width="1918" height="1017" alt="Screenshot 2026-05-11 142811" src="https://github.com/user-attachments/assets/fd17e58f-f178-4cfd-b411-fc5aa1ef9789" />
<img width="1918" height="1020" alt="Screenshot 2026-05-11 142744" src="https://github.com/user-attachments/assets/daaa7f2c-9a39-438f-9cea-4f4cbb764a41" />
<img width="1918" height="1017" alt="Screenshot 2026-05-11 142828" src="https://github.com/user-attachments/assets/030ae762-5e22-4eac-a6d6-650e2becee79" />
<img width="1918" height="1017" alt="Screenshot 2026-05-11 142905" src="https://github.com/user-attachments/assets/60e5b61c-87a0-48df-b134-2ffb8c307c27" />
<img width="1918" height="1021" alt="Screenshot 2026-05-11 142926" src="https://github.com/user-attachments/assets/6e77cb5e-8cff-4c30-9437-92a6fa71f708" />
<img width="1918" height="1018" alt="Screenshot 2026-05-11 142943" src="https://github.com/user-attachments/assets/cb43867c-fd12-4bfb-bef1-1e700dfbdfb1" />
<img width="1918" height="1022" alt="Screenshot 2026-05-11 143002" src="https://github.com/user-attachments/assets/a756acd7-30cf-4be4-85e4-4258b5a65b57" />
<img width="1918" height="1017" alt="Screenshot 2026-05-11 143017" src="https://github.com/user-attachments/assets/fd01e454-e458-4526-a9ba-25ec381dfeb8" />
<img width="1917" height="1017" alt="Screenshot 2026-05-11 143041" src="https://github.com/user-attachments/assets/f0186922-12a0-499d-aabb-233106f2284a" />


---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3 |
| GUI Framework | Tkinter (`tk`, `ttk`) |
| Styling | Custom dark theme via Tkinter color palette + `ttk.Style` (clam theme) |
| Data Storage | JSON flat file (`mentor_mentee_data.json`) |
| Export | Python `csv` module |
| Unique IDs | Python `uuid` module |
| Date Handling | Python `datetime` module — includes custom popup `DatePicker` calendar widget |
| Standard Library | `os`, `json`, `uuid`, `random`, `math`, `csv`, `re`, `datetime` |

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Tkinter (included with standard Python on Windows & macOS; see note for Linux)

> **Linux users:** Install Tkinter via `sudo apt install python3-tk`

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/mentorlink.git

# Navigate into the project directory
cd mentorlink

# No external dependencies required — uses Python standard library only

# Run the application
python PRPSLA.py
```

> Data is automatically saved to `mentor_mentee_data.json` in the same directory.

---

## Project Structure

```
mentorlink/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   ├── Mentors/
│   │   ├── Mentees/
│   │   ├── Sessions/
│   │   ├── Goals/
│   │   └── Matching/
│   ├── data/
│   ├── utils/
│   └── App.js
├── public/
├── screenshots/
├── package.json
└── README.md
```

---

## Data & Modules

### Sample Data (from screenshots)

**Mentors (6 total)**
| Name | Expertise | Field | Experience |
|------|-----------|-------|------------|
| Ms. Priti Bhokariya | Python, IoT | Engineering | 10–15 years |
| Ms. Sharyu Kadam | IoT, Workshop | Engineering | 10–15 years |
| Ms. Neha More | Fundamentals of OS | Design | 10–15 years |
| Ms. Prachi Arora | Electronics, Microprocessor | Engineering | 20+ years |
| Mr. Siddesh Masurdkar | Computer Networks | Engineering | 6–10 years |
| Ms. Rupali Pawar | Personal Skill Development | Engineering | 6–10 years |

**Mentees (9 total)**
| Name | Learning Goal | Field |
|------|--------------|-------|
| Vedant Gohil | Patience | Engineering |
| Mohak Mehta | Self Confidence | Design |
| Parv Khichadia | Linux OS | Data Science |
| Mohammad Hashim Balsari | Router & Switch Configuration | Engineering |
| Krishna Bundhiya | IoT | Product |
| Sharvil Khaple | Workshop | Finance |
| Om Kshringar | Microcontroller | Data Science |
| Krish Hingu | Python | Design |
| Preet Mehta | Public Speaking | Law |

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Please follow the existing code style and include screenshots for UI changes.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- Built for **SVKM's Student Business Mentoring Program (SBMP)**
- Designed with ❤️ to make mentorship structured, measurable, and impactful

---

*v3.0 · MentorLink*
