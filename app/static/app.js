(function () {
  const API_BASE = "/api";

  const userIdInput = document.getElementById("userId");
  const uploadForm = document.getElementById("uploadForm");
  const askForm = document.getElementById("askForm");
  const deleteBtn = document.getElementById("deleteData");
  const statusEl = document.getElementById("status");
  const answerBox = document.getElementById("answerBox");

  function getOrCreateUserId() {
    let id = localStorage.getItem("scholar_user_id");
    if (!id) {
      id = (window.crypto && crypto.randomUUID)
        ? `user_${crypto.randomUUID()}`
        : `user_${Math.random().toString(36).slice(2, 10)}_${Date.now()}`;
      localStorage.setItem("scholar_user_id", id);
    }
    if (userIdInput) userIdInput.value = id;
    return id;
  }

  function currentUserId() {
    return userIdInput?.value || getOrCreateUserId();
  }

  function setStatus(msg, isError = false) {
    if (!statusEl) return;
    statusEl.textContent = msg || "";
    statusEl.style.color = isError ? "#f87171" : "#94a3b8";
  }

  async function safeJson(res) {
    try {
      return await res.json();
    } catch {
      return {};
    }
  }

  getOrCreateUserId();

  uploadForm?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById("pdfFile");
    const file = fileInput?.files?.[0];

    if (!file) {
      setStatus("Please select a PDF file.", true);
      return;
    }

    const submitBtn = uploadForm.querySelector("button[type='submit']");
    const originalText = submitBtn?.textContent || "Upload + Index";
    if (submitBtn) submitBtn.textContent = "Uploading...";

    const formData = new FormData();
    formData.append("pdf", file); // backend expects 'pdf'
    formData.append("user_id", currentUserId());

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await safeJson(res);
      if (!res.ok) {
        setStatus(data.error || "Upload failed.", true);
        return;
      }

      setStatus(data.message || "PDF indexed successfully.");
    } catch {
      setStatus("Network error during upload.", true);
    } finally {
      if (submitBtn) submitBtn.textContent = originalText;
    }
  });

  askForm?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const questionInput = document.getElementById("question");
    const question = questionInput?.value?.trim();

    if (!question) {
      setStatus("Please enter a question.", true);
      return;
    }

    const submitBtn = askForm.querySelector("button[type='submit']");
    const originalText = submitBtn?.textContent || "Ask ScholarAI";
    if (submitBtn) submitBtn.textContent = "Thinking...";

    if (answerBox) answerBox.textContent = "Thinking...";
    setStatus("");

    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          user_id: currentUserId(),
        }),
      });

      const data = await safeJson(res);
      if (!res.ok) {
        if (answerBox) answerBox.textContent = "No answer yet.";
        setStatus(data.error || "Failed to fetch answer.", true);
        return;
      }

      if (answerBox) answerBox.textContent = data.answer || "No answer returned.";
      setStatus("Answer ready.");
    } catch {
      if (answerBox) answerBox.textContent = "Network error.";
      setStatus("Could not reach server.", true);
    } finally {
      if (submitBtn) submitBtn.textContent = originalText;
    }
  });

  deleteBtn?.addEventListener("click", async () => {
    const userId = currentUserId();
    const ok = window.confirm("Delete all indexed data for your current session?");
    if (!ok) return;

    setStatus("Deleting data...");

    try {
      const res = await fetch(`${API_BASE}/user/${encodeURIComponent(userId)}`, {
        method: "DELETE",
      });

      const data = await safeJson(res);
      if (!res.ok) {
        setStatus(data.error || "Delete failed.", true);
        return;
      }

      if (answerBox) answerBox.textContent = "No answer yet.";
      setStatus(data.message || "Data deleted.");
    } catch {
      setStatus("Network error during delete.", true);
    }
  });
})();