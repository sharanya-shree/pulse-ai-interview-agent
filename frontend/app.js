const state = {
  candidates: [],
  selectedCandidate: null,
  sessionId: null,
  questionCount: 0,
  isLoading: false,
  currentInterviewStarted: false,
  error: null,
};

const TOTAL_QUESTIONS = 10;

const elements = {
  selectionPanel: document.getElementById("selectionPanel"),
  interviewPanel: document.getElementById("interviewPanel"),
  completionPanel: document.getElementById("completionPanel"),
  candidateGrid: document.getElementById("candidateGrid"),
  candidateSummary: document.getElementById("candidateSummary"),
  summaryName: document.getElementById("summaryName"),
  summaryBadge: document.getElementById("summaryBadge"),
  summaryRole: document.getElementById("summaryRole"),
  summaryExperience: document.getElementById("summaryExperience"),
  summaryDays: document.getElementById("summaryDays"),
  summaryText: document.getElementById("summaryText"),
  startInterviewButton: document.getElementById("startInterviewButton"),
  newInterviewButton: document.getElementById("newInterviewButton"),
  restartInterviewButton: document.getElementById("restartInterviewButton"),
  finishNewInterviewButton: document.getElementById("finishNewInterviewButton"),
  interviewTitle: document.getElementById("interviewTitle"),
  progressLabel: document.getElementById("progressLabel"),
  progressPercent: document.getElementById("progressPercent"),
  progressBar: document.getElementById("progressBar"),
  messageList: document.getElementById("messageList"),
  answerForm: document.getElementById("answerForm"),
  answerInput: document.getElementById("answerInput"),
  submitAnswerButton: document.getElementById("submitAnswerButton"),
  formHint: document.getElementById("formHint"),
  feedbackContent: document.getElementById("feedbackContent"),
};

function setError(message) {
  state.error = message;
  renderError();
}

function clearError() {
  state.error = null;
  renderError();
}

/*
 * Browser navigation
 *
 * The application is a single-page UI, so switching from the
 * candidate-selection panel to the interview panel does not
 * automatically create a browser history entry.
 *
 * We use the URL hash:
 *
 * Candidate selection:
 * https://your-site.vercel.app/
 *
 * Interview:
 * https://your-site.vercel.app/#interview
 *
 * This allows the browser Back button to return to candidate
 * selection and Forward to return to the interview.
 */
function setAppRoute(route, { replace = false } = {}) {
  const hash = route === "interview" ? "#interview" : "";

  const url =
    `${window.location.pathname}` + `${window.location.search}` + hash;

  const historyState = {
    view: route,
  };

  if (replace) {
    window.history.replaceState(historyState, "", url);
  } else {
    window.history.pushState(historyState, "", url);
  }
}

function handleBrowserNavigation() {
  const route = window.location.hash;

  if (route === "#interview") {
    /*
     * If the interview is already active in this browser session,
     * restore the interview panel when the user presses Forward.
     */
    if (state.selectedCandidate && state.currentInterviewStarted) {
      showInterviewView();
      return;
    }

    /*
     * If somebody directly opens /#interview or refreshes it,
     * the interview state cannot be restored because it is stored
     * only in memory.
     *
     * Therefore safely return to candidate selection.
     */
    setAppRoute("selection", { replace: true });
    showCandidateSelection();
    return;
  }

  /*
   * Empty hash = candidate-selection view.
   *
   * We intentionally do not reset the interview state here.
   * This means:
   *
   * Back     -> candidate selection
   * Forward  -> interview again
   */
  showCandidateSelection();
}

function getActivePanel() {
  if (!elements.interviewPanel.classList.contains("hidden")) {
    return elements.interviewPanel;
  }

  if (!elements.completionPanel.classList.contains("hidden")) {
    return elements.completionPanel;
  }

  return elements.selectionPanel;
}

function renderError() {
  document.querySelectorAll(".error-banner").forEach((node) => node.remove());

  if (!state.error) {
    return;
  }

  const errorNode = document.createElement("div");

  errorNode.className = "error-banner";
  errorNode.textContent = state.error;

  getActivePanel().appendChild(errorNode);
}

function buildSessionId(candidate) {
  if (candidate?.member?.id) {
    return `demo-${candidate.member.id
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")}-${Date.now()}`;
  }

  return `demo-session-${Date.now()}`;
}

function createCandidateCard(candidate) {
  const member = candidate.member || {};

  const isSelected = state.selectedCandidate?.member?.id === member.id;

  const completedDays = (candidate.missions || [])
    .filter((mission) => mission.passed)
    .map((mission) => mission.day);

  const card = document.createElement("button");

  card.type = "button";

  card.className = `candidate-card${isSelected ? " selected" : ""}`;

  card.innerHTML = `
    <h3>${member.name || "Candidate"}</h3>

    <p>
      ${member.jobRole || "Role pending"}
    </p>

    <p>
      ${
        member.yearsExperience != null
          ? `${member.yearsExperience} years experience`
          : "Experience pending"
      }
    </p>

    <p>
      ${
        completedDays.length
          ? `${completedDays.length} completed days`
          : "Learning path pending"
      }
    </p>
  `;

  card.addEventListener("click", () => {
    state.selectedCandidate = candidate;

    renderCandidateSelection();
    renderCandidateSummary();
  });

  return card;
}

function renderCandidateSelection() {
  elements.candidateGrid.innerHTML = "";

  state.candidates.forEach((candidate) => {
    elements.candidateGrid.appendChild(createCandidateCard(candidate));
  });
}

function renderCandidateSummary() {
  if (!state.selectedCandidate) {
    elements.candidateSummary.classList.add("hidden");
    return;
  }

  const member = state.selectedCandidate.member || {};

  const missions = state.selectedCandidate.missions || [];

  const completedDays = missions
    .filter((mission) => mission.passed)
    .map((mission) => mission.day);

  const summaryText =
    `${member.name || "Candidate"} is a ` +
    `${member.jobRole || "professional"} with ` +
    `${
      member.yearsExperience != null ? member.yearsExperience : "a growing"
    } ` +
    `years of experience. Their learning profile highlights ` +
    `${completedDays.length} completed milestones and strong momentum ` +
    `across the curriculum.`;

  elements.summaryName.textContent = member.name || "Candidate";

  elements.summaryBadge.textContent = "Ready to interview";

  elements.summaryRole.textContent = member.jobRole || "Role pending";

  elements.summaryExperience.textContent =
    member.yearsExperience != null
      ? `${member.yearsExperience} years`
      : "Pending";

  elements.summaryDays.textContent = completedDays.length
    ? completedDays.slice(0, 6).join(", ")
    : "None";

  elements.summaryText.textContent = `${summaryText}${
    member.education ? ` Education: ${member.education}.` : ""
  }`;

  elements.candidateSummary.classList.remove("hidden");
}

function resetInterviewView() {
  elements.messageList.innerHTML = "";

  elements.answerInput.value = "";

  elements.answerForm.classList.remove("hidden");

  elements.interviewPanel.classList.add("hidden");

  elements.completionPanel.classList.add("hidden");

  elements.selectionPanel.classList.remove("hidden");

  state.currentInterviewStarted = false;

  state.sessionId = null;

  state.questionCount = 0;

  elements.progressLabel.textContent = `Question 0 of ${TOTAL_QUESTIONS}`;

  elements.progressPercent.textContent = "0%";

  elements.progressBar.style.width = "0%";

  elements.interviewTitle.textContent = "Interview in progress";

  elements.feedbackContent.innerHTML = "";

  clearError();
}

function showInterviewView() {
  elements.selectionPanel.classList.add("hidden");

  elements.interviewPanel.classList.remove("hidden");

  elements.completionPanel.classList.add("hidden");

  elements.answerForm.classList.remove("hidden");

  elements.submitAnswerButton.disabled = false;

  elements.answerInput.disabled = false;

  elements.answerInput.focus();
}

function showCandidateSelection() {
  elements.selectionPanel.classList.remove("hidden");

  elements.interviewPanel.classList.add("hidden");

  elements.completionPanel.classList.add("hidden");

  /*
   * Keep the selected candidate summary visible when returning
   * with the browser Back button.
   */
  if (state.selectedCandidate) {
    elements.candidateSummary.classList.remove("hidden");
  } else {
    elements.candidateSummary.classList.add("hidden");
  }

  elements.answerForm.classList.add("hidden");
}

function showCompletionView() {
  elements.selectionPanel.classList.add("hidden");

  elements.interviewPanel.classList.add("hidden");

  elements.completionPanel.classList.remove("hidden");

  elements.answerForm.classList.add("hidden");
}

function renderProgress() {
  const count = Math.min(Math.max(state.questionCount, 0), TOTAL_QUESTIONS);

  const percent = Math.round((count / TOTAL_QUESTIONS) * 100);

  elements.progressLabel.textContent = `Question ${count} of ${TOTAL_QUESTIONS}`;

  elements.progressPercent.textContent = `${percent}%`;

  elements.progressBar.style.width = `${percent}%`;
}

function appendMessage(role, content) {
  const bubble = document.createElement("div");

  bubble.className = `message-bubble ${role}`;

  bubble.textContent = content;

  elements.messageList.appendChild(bubble);
}

function renderFeedback(feedback) {
  if (!feedback) {
    elements.feedbackContent.innerHTML = `
      <div class="feedback-card">
        <h3>No feedback available</h3>

        <p>
          The interview ended without structured feedback.
        </p>
      </div>
    `;

    return;
  }

  const cards = [
    {
      title: "Summary",

      items: feedback.summary ? [feedback.summary] : [],
    },

    {
      title: "Strengths",

      items: feedback.strengths || [],
    },

    {
      title: "Gaps",

      items: feedback.gaps || [],
    },

    {
      title: "Next",

      items: feedback.next || [],
    },
  ];

  elements.feedbackContent.innerHTML = cards
    .map((card) => {
      const items = card.items.length ? card.items : ["None recorded"];

      const list = items.map((item) => `<li>${item}</li>`).join("");

      return `
        <div class="feedback-card">
          <h3>${card.title}</h3>

          <ul>
            ${list}
          </ul>
        </div>
      `;
    })
    .join("");
}

async function loadCandidates() {
  try {
    const payload = await requestJson("/api/candidates");

    state.candidates = payload.candidates || [];

    if (!state.candidates.length) {
      throw new Error("No candidates were returned by the backend.");
    }

    renderCandidateSelection();

    if (!state.selectedCandidate) {
      state.selectedCandidate = state.candidates[0];

      renderCandidateSummary();
    }
  } catch (error) {
    setError(error.message || "Unable to load candidates from the backend.");
  }
}

async function startInterview() {
  if (!state.selectedCandidate) {
    setError("Choose a candidate before starting the interview.");

    return;
  }

  state.isLoading = true;

  elements.startInterviewButton.disabled = true;

  elements.submitAnswerButton.disabled = true;

  elements.formHint.textContent = "Starting interview…";

  clearError();

  try {
    const requestBody = {
      sessionId: buildSessionId(state.selectedCandidate),

      candidate: {
        id: state.selectedCandidate.member?.id,

        name: state.selectedCandidate.member?.name,

        experienceLevel: state.selectedCandidate.member?.jobRole,

        completedDays: (state.selectedCandidate.missions || [])
          .filter((mission) => mission.passed)
          .map((mission) => mission.day),

        jobRole: state.selectedCandidate.member?.jobRole,

        yearsExperience: state.selectedCandidate.member?.yearsExperience,

        education: state.selectedCandidate.member?.education,
      },
    };

    const payload = await requestJson("/api/interview", {
      method: "POST",

      body: JSON.stringify(requestBody),
    });

    state.sessionId = requestBody.sessionId;

    state.currentInterviewStarted = true;

    /*
     * IMPORTANT:
     *
     * Add a browser history entry only after
     * the backend successfully starts the interview.
     *
     * Now:
     *
     * Candidate page
     *       ↓
     * Interview page
     *       ↓
     * Browser Back
     *       ↓
     * Candidate page
     */
    setAppRoute("interview");

    /*
     * The first response from the backend
     * is already Question 1.
     */
    state.questionCount = 1;

    showInterviewView();

    elements.interviewTitle.textContent = `Interview with ${
      state.selectedCandidate.member?.name || "candidate"
    }`;

    appendMessage(
      "system",
      "Interview started. The interviewer will ask a series of technical questions.",
    );

    appendMessage("assistant", payload.reply || "Welcome! Let us begin.");

    elements.formHint.textContent =
      "Submit your first answer to continue the interview.";

    renderProgress();
  } catch (error) {
    setError(error.message || "Unable to start the interview.");
  } finally {
    state.isLoading = false;

    elements.startInterviewButton.disabled = false;

    elements.submitAnswerButton.disabled = false;
  }
}

async function submitAnswer(event) {
  event.preventDefault();

  if (state.isLoading || !state.currentInterviewStarted || !state.sessionId) {
    return;
  }

  const answer = elements.answerInput.value.trim();

  if (!answer) {
    setError("Enter an answer before submitting.");

    return;
  }

  state.isLoading = true;

  elements.submitAnswerButton.disabled = true;

  elements.answerInput.disabled = true;

  elements.formHint.textContent = "Submitting answer…";

  clearError();

  try {
    const payload = await requestJson("/api/interview", {
      method: "POST",

      body: JSON.stringify({
        sessionId: state.sessionId,

        message: answer,
      }),
    });

    appendMessage("user", answer);

    appendMessage("assistant", payload.reply || "Thanks for your response.");

    /*
     * If the backend says the interview is done,
     * do not increase the question count again.
     */
    if (payload.done) {
      state.currentInterviewStarted = false;

      showCompletionView();

      elements.interviewTitle.textContent = "Interview complete";

      renderFeedback(payload.feedback);

      elements.formHint.textContent =
        "The interview is complete. You can start another one.";
    } else {
      /*
       * The backend has returned the NEXT question.
       * Therefore increment the question number.
       */
      state.questionCount = Math.min(state.questionCount + 1, TOTAL_QUESTIONS);

      renderProgress();

      elements.answerInput.value = "";

      elements.answerInput.disabled = false;

      elements.formHint.textContent =
        "Answer the next question when you are ready.";
    }
  } catch (error) {
    setError(error.message || "Unable to submit the answer.");
  } finally {
    state.isLoading = false;

    elements.submitAnswerButton.disabled = false;

    elements.answerInput.disabled = false;
  }
}

function attachEvents() {
  elements.startInterviewButton.addEventListener("click", startInterview);

  elements.restartInterviewButton.addEventListener("click", () => {
    resetInterviewView();

    /*
     * Replace instead of push because this is
     * an intentional "start over" action.
     */
    setAppRoute("selection", {
      replace: true,
    });

    showCandidateSelection();
  });

  elements.newInterviewButton.addEventListener("click", () => {
    resetInterviewView();

    setAppRoute("selection", {
      replace: true,
    });

    showCandidateSelection();
  });

  elements.finishNewInterviewButton.addEventListener("click", () => {
    resetInterviewView();

    setAppRoute("selection", {
      replace: true,
    });

    showCandidateSelection();
  });

  /*
   * Listen for Chrome/Edge/Firefox Back and Forward buttons.
   */
  window.addEventListener("popstate", handleBrowserNavigation);

  elements.answerForm.addEventListener("submit", submitAnswer);
}

function initialize() {
  attachEvents();

  /*
   * A fresh page load starts at candidate selection.
   *
   * If someone manually opens /#interview,
   * handleBrowserNavigation() will safely return
   * them to candidate selection because the interview
   * state only exists in memory.
   */
  if (window.location.hash !== "#interview") {
    setAppRoute("selection", {
      replace: true,
    });
  }

  renderCandidateSelection();

  renderCandidateSummary();

  loadCandidates();

  /*
   * Restore the correct panel for the current
   * browser route.
   */
  handleBrowserNavigation();
}

initialize();
