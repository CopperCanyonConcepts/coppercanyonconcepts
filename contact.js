(() => {
  const RECIPIENT = "operations@coppercanyonconcepts.com";
  const MAX_MAILTO_LENGTH = 1900;

  function clean(value) {
    return String(value || "").replace(/\r\n?/g, "\n").trim();
  }

  function addSection(lines, label, value) {
    const cleaned = clean(value);
    if (!cleaned) return;
    lines.push(`${label}:`);
    lines.push(cleaned);
    lines.push("");
  }

  document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#inquiry-form");
    const status = document.querySelector("#form-status");
    const areaError = document.querySelector("#help-area-error");
    const areaGroup = document.querySelector(".checkbox_fieldset");
    const submitButton = form?.querySelector('button[type="submit"]');
    const copyFallback = document.querySelector("#copy-fallback");
    const copyText = document.querySelector("#prepared-inquiry");
    const copyButton = document.querySelector("#copy-inquiry");
    if (!form || !status || !areaError || !areaGroup || !submitButton || !copyFallback || !copyText || !copyButton) return;

    submitButton.disabled = false;

    const areaInputs = Array.from(form.querySelectorAll('input[name="help_areas"]'));

    function selectedAreas() {
      return areaInputs.filter(input => input.checked).map(input => input.value);
    }

    function validateAreas() {
      const valid = selectedAreas().length > 0;
      areaError.hidden = valid;
      areaGroup.setAttribute("aria-invalid", String(!valid));
      areaInputs[0]?.setAttribute("aria-invalid", String(!valid));
      return valid;
    }

    areaInputs.forEach(input => {
      input.addEventListener("change", () => {
        if (selectedAreas().length > 0) {
          areaError.hidden = true;
          areaGroup.setAttribute("aria-invalid", "false");
          areaInputs[0]?.setAttribute("aria-invalid", "false");
        }
      });
    });

    copyButton.addEventListener("click", async () => {
      let copied = false;
      if (navigator.clipboard && window.isSecureContext) {
        try {
          await navigator.clipboard.writeText(copyText.value);
          copied = true;
        } catch {
          copied = false;
        }
      }
      if (!copied) {
        copyText.focus();
        copyText.select();
        copied = document.execCommand("copy");
      }
      status.textContent = copied
        ? "The prepared inquiry was copied. Paste it into an email to operations@coppercanyonconcepts.com."
        : "Select the prepared inquiry and copy it manually into an email to operations@coppercanyonconcepts.com.";
    });

    form.addEventListener("submit", event => {
      event.preventDefault();
      status.textContent = "";
      copyFallback.hidden = true;

      const areasValid = validateAreas();
      if (!form.reportValidity() || !areasValid) {
        if (!areasValid) areaInputs[0]?.focus();
        status.textContent = "Please complete the required fields before preparing the inquiry.";
        return;
      }

      const data = new FormData(form);
      const contactName = clean(data.get("contact_name"));
      const email = clean(data.get("email"));
      const company = clean(data.get("company"));
      const businessStage = clean(data.get("business_stage"));
      const timeframe = clean(data.get("timeframe"));
      const subjectIdentity = company || contactName || "website visitor";
      const subject = `Business inquiry from ${subjectIdentity}`;
      const lines = [
        "Copper Canyon Concepts business inquiry",
        "",
        `Contact name: ${contactName}`,
        `Reply email: ${email}`,
        `Company or business: ${company || "Not provided"}`,
        `Business stage: ${businessStage}`,
        `Preferred timeframe: ${timeframe || "Not specified"}`,
        `Help areas: ${selectedAreas().join(", ")}`,
        "",
      ];

      addSection(lines, "Problem to solve", data.get("problem"));
      addSection(lines, "Current tools or systems", data.get("current_tools"));
      addSection(lines, "Desired result", data.get("desired_result"));
      lines.push("The sender confirmed that this inquiry does not intentionally include passwords, payment information, confidential customer records, health information, or other sensitive data.");

      const preparedText = lines.join("\n");
      const mailto = `mailto:${RECIPIENT}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(preparedText)}`;
      if (mailto.length > MAX_MAILTO_LENGTH) {
        copyText.value = preparedText;
        copyFallback.hidden = false;
        status.textContent = "The inquiry is too detailed for a reliable email link. Use the local copy option below so no information is truncated.";
        copyButton.focus();
        return;
      }
      status.textContent = "Your email app is opening with the inquiry prepared. Review the message before sending.";
      window.location.href = mailto;
    });
  });
})();
