(() => {
    const textarea = document.querySelector(
        '.yuki-content-editor textarea[name="content"]',
    );

    if (!textarea) {
        return;
    }

    const fieldRow = textarea.closest(".form-row");

    if (!fieldRow || fieldRow.dataset.markdownEditorReady) {
        return;
    }

    fieldRow.dataset.markdownEditorReady = "true";

    const toolbar = document.createElement("div");
    toolbar.className = "yuki-markdown-toolbar";
    toolbar.innerHTML = `
        <div class="yuki-markdown-toolbar__tabs" role="tablist">
            <button type="button" class="is-active" data-yuki-md-mode="write">撰写</button>
            <button type="button" data-yuki-md-mode="preview">预览</button>
        </div>
        <div class="yuki-markdown-toolbar__tools">
            <button type="button" data-yuki-md-insert="image">图片</button>
            <button type="button" data-yuki-md-insert="formula">公式</button>
            <button type="button" data-yuki-md-insert="code">代码</button>
        </div>
    `;

    const preview = document.createElement("div");
    preview.className = "yuki-markdown-preview";
    preview.hidden = true;

    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = "image/*";
    fileInput.className = "yuki-markdown-file";
    fileInput.hidden = true;

    textarea.parentNode.insertBefore(
        toolbar,
        textarea,
    );
    toolbar.insertAdjacentElement(
        "afterend",
        fileInput,
    );
    textarea.insertAdjacentElement(
        "afterend",
        preview,
    );

    const tabs = toolbar.querySelectorAll("[data-yuki-md-mode]");
    const insertButtons = toolbar.querySelectorAll("[data-yuki-md-insert]");

    const setMode = (mode) => {
        tabs.forEach((button) => {
            button.classList.toggle(
                "is-active",
                button.dataset.yukiMdMode === mode,
            );
        });

        textarea.hidden = mode === "preview";
        preview.hidden = mode !== "preview";

        if (mode === "preview") {
            preview.innerHTML = renderMarkdown(textarea.value);
            renderMath(preview);
        }
    };

    tabs.forEach((button) => {
        button.addEventListener(
            "click",
            () => setMode(button.dataset.yukiMdMode),
        );
    });

    insertButtons.forEach((button) => {
        button.addEventListener(
            "click",
            () => {
                if (button.dataset.yukiMdInsert === "image") {
                    fileInput.click();
                    return;
                }

                insertSnippet(button.dataset.yukiMdInsert);
            },
        );
    });

    fileInput.addEventListener(
        "change",
        () => {
            const [file] = fileInput.files || [];

            if (file) {
                uploadImage(file);
            }

            fileInput.value = "";
        },
    );

    textarea.addEventListener(
        "input",
        () => {
            if (!preview.hidden) {
                preview.innerHTML = renderMarkdown(textarea.value);
                renderMath(preview);
            }
        },
    );

    function insertSnippet(type) {
        const snippets = {
            formula: "$$\\nE = mc^2\\n$$",
            code: "```python\\nprint(\"Hello, Yuki\")\\n```",
        };
        const snippet = snippets[type] || "";
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const before = textarea.value.slice(
            0,
            start,
        );
        const after = textarea.value.slice(end);
        const prefix = before && !before.endsWith("\n")
            ? "\n\n"
            : "";
        const suffix = after && !after.startsWith("\n")
            ? "\n\n"
            : "";

        textarea.value = `${before}${prefix}${snippet}${suffix}${after}`;
        textarea.focus();

        const cursor = before.length + prefix.length + snippet.length;
        textarea.setSelectionRange(
            cursor,
            cursor,
        );
        textarea.dispatchEvent(
            new Event(
                "input",
                {
                    bubbles: true,
                },
            ),
        );
    }

    async function uploadImage(file) {
        const imageButton = toolbar.querySelector(
            '[data-yuki-md-insert="image"]',
        );
        const originalText = imageButton.textContent;
        const formData = new FormData();

        formData.append(
            "image",
            file,
        );

        imageButton.disabled = true;
        imageButton.textContent = "上传中";

        try {
            const response = await fetch(
                "/admin/markdown-image-upload/",
                {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                },
            );
            const payload = await response.json();

            if (!response.ok) {
                throw new Error(payload.error || "图片上传失败。");
            }

            insertText(payload.markdown);
        } catch (error) {
            window.alert(error.message);
        } finally {
            imageButton.disabled = false;
            imageButton.textContent = originalText;
        }
    }

    function renderMarkdown(source) {
        const blocks = source
            .replace(/\r\n/g, "\n")
            .split(/\n{2,}/);

        return blocks
            .map(renderBlock)
            .join("");
    }

    function renderBlock(block) {
        const text = block.trim();

        if (!text) {
            return "";
        }

        if (/^```/.test(text)) {
            return renderCodeBlock(text);
        }

        if (/^\$\$/.test(text)) {
            return `<p class="md-formula">$$${escapeHtml(
                text.replace(/^\$\$|\$\$$/g, "").trim(),
            )}$$</p>`;
        }

        if (/^#{1,6}\s/.test(text)) {
            const level = text.match(/^#{1,6}/)[0].length;
            return `<h${level}>${renderInline(text.replace(/^#{1,6}\s+/, ""))}</h${level}>`;
        }

        if (/^\|.+\|$/m.test(text)) {
            return renderTable(text);
        }

        if (/^[-*]\s/m.test(text)) {
            const items = text
                .split("\n")
                .filter(Boolean)
                .map((line) => `<li>${renderInline(line.replace(/^[-*]\s+/, ""))}</li>`)
                .join("");

            return `<ul>${items}</ul>`;
        }

        if (/^\d+\.\s/m.test(text)) {
            const items = text
                .split("\n")
                .filter(Boolean)
                .map((line) => `<li>${renderInline(line.replace(/^\d+\.\s+/, ""))}</li>`)
                .join("");

            return `<ol>${items}</ol>`;
        }

        return `<p>${renderInline(text).replace(/\n/g, "<br>")}</p>`;
    }

    function renderCodeBlock(text) {
        const code = text
            .replace(/^```[a-zA-Z0-9_-]*\n?/, "")
            .replace(/```$/, "");

        return `<pre><code>${escapeHtml(code)}</code></pre>`;
    }

    function renderTable(text) {
        const rows = text
            .split("\n")
            .map((row) => row.trim())
            .filter(Boolean)
            .filter((row) => !/^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(row));

        if (!rows.length) {
            return "";
        }

        const [head, ...body] = rows.map(splitTableRow);
        const thead = `<thead><tr>${head
            .map((cell) => `<th>${renderInline(cell)}</th>`)
            .join("")}</tr></thead>`;
        const tbody = `<tbody>${body
            .map((row) => `<tr>${row
                .map((cell) => `<td>${renderInline(cell)}</td>`)
                .join("")}</tr>`)
            .join("")}</tbody>`;

        return `<table>${thead}${tbody}</table>`;
    }

    function splitTableRow(row) {
        return row
            .replace(/^\|/, "")
            .replace(/\|$/, "")
            .split("|")
            .map((cell) => cell.trim());
    }

    function renderInline(text) {
        let html = escapeHtml(text);

        html = html.replace(
            /!\[([^\]]*)\]\(([^)]+)\)/g,
            '<img src="$2" alt="$1">',
        );
        html = html.replace(
            /\[([^\]]+)\]\(([^)]+)\)/g,
            '<a href="$2">$1</a>',
        );
        html = html.replace(
            /`([^`]+)`/g,
            "<code>$1</code>",
        );
        html = html.replace(
            /\*\*([^*]+)\*\*/g,
            "<strong>$1</strong>",
        );
        html = html.replace(
            /\*([^*]+)\*/g,
            "<em>$1</em>",
        );
        html = html.replace(
            /~~([^~]+)~~/g,
            "<del>$1</del>",
        );
        html = html.replace(
            /\$([^$]+)\$/g,
            '<span class="md-formula-inline">\\($1\\)</span>',
        );

        return html;
    }

    function renderMath(root) {
        if (typeof window.renderMathInElement !== "function") {
            return;
        }

        window.renderMathInElement(
            root,
            {
                delimiters: [
                    {
                        left: "$$",
                        right: "$$",
                        display: true,
                    },
                    {
                        left: "$",
                        right: "$",
                        display: false,
                    },
                    {
                        left: "\\(",
                        right: "\\)",
                        display: false,
                    },
                    {
                        left: "\\[",
                        right: "\\]",
                        display: true,
                    },
                ],
                throwOnError: false,
            },
        );
    }

    function insertText(text) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const before = textarea.value.slice(
            0,
            start,
        );
        const after = textarea.value.slice(end);
        const prefix = before && !before.endsWith("\n")
            ? "\n\n"
            : "";
        const suffix = after && !after.startsWith("\n")
            ? "\n\n"
            : "";

        textarea.value = `${before}${prefix}${text}${suffix}${after}`;
        textarea.focus();

        const cursor = before.length + prefix.length + text.length;
        textarea.setSelectionRange(
            cursor,
            cursor,
        );
        textarea.dispatchEvent(
            new Event(
                "input",
                {
                    bubbles: true,
                },
            ),
        );
    }

    function getCookie(name) {
        return document.cookie
            .split(";")
            .map((cookie) => cookie.trim())
            .find((cookie) => cookie.startsWith(`${name}=`))
            ?.split("=")
            .slice(1)
            .join("=") || "";
    }

    function escapeHtml(value) {
        return value.replace(
            /[&<>"']/g,
            (char) => ({
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;",
            })[char],
        );
    }
})();
