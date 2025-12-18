(function() {
    // 定义显示提示框函数
    function showPrompt(message, duration = 1500) {
        var promptBox = document.createElement('div');
        promptBox.style.position = 'fixed';
        promptBox.style.top = '20px';
        promptBox.style.left = '50%';
        promptBox.style.transform = 'translateX(-50%)';
        promptBox.style.padding = '10px';
        promptBox.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        promptBox.style.color = 'white';
        promptBox.style.borderRadius = '5px';
        promptBox.style.zIndex = '10000';
        promptBox.innerHTML = message;
        document.body.appendChild(promptBox);
        setTimeout(() => {
            document.body.removeChild(promptBox);
        }, duration);
    }

    // 定义复制代码函数
    function copyCode(code, successMessage) {
        var textarea = document.createElement('textarea');
        textarea.value = code;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            var successful = document.execCommand('copy');
            if (successful) {
                showPrompt(successMessage);
            }
        } catch (err) {
            console.error('Failed to copy', err);
        }
        document.body.removeChild(textarea);
    }

    // 初始化代码工具
    function initCodeTools() {
        var codeTools = document.getElementById("zxsq-markdown-code-tools");
        var show = codeTools.querySelector(".show").innerText;
        var hide = codeTools.querySelector(".hide").innerText;
        var copy = codeTools.querySelector(".copy").innerText;
        var copysucc = codeTools.querySelector(".copysucc").innerText;

        document.querySelectorAll("pre").forEach((pre) => {
            if (pre.firstChild.className === "hideCode" || pre.firstChild.className === "CopyMyCode" || pre.firstChild.className === "showCode") {
                return;
            }
            // 创建一个容器来放置两个按钮
            var buttonContainer = document.createElement('div');
            buttonContainer.style.display = 'flex';
            buttonContainer.style.justifyContent = 'flex-start';
            buttonContainer.style.alignItems = 'center';
            buttonContainer.style.marginBottom = '10px';

            var copyCodeButton = document.createElement('em');
            copyCodeButton.className = "CopyMyCode";
            copyCodeButton.style = "cursor:pointer;font-size:12px;color:#369 !important;margin-right:10px;";
            copyCodeButton.innerText = copy;
            buttonContainer.appendChild(copyCodeButton);
            copyCodeButton.onclick = function() {
                var code = this.parentElement.parentElement.lastChild.innerText;
                copyCode(code, copysucc);
            };

            var hideCode = document.createElement('em');
            hideCode.className = "hideCode";
            hideCode.style = "cursor:pointer;font-size:12px;color:#369 !important;";
            hideCode.innerText = hide;
            buttonContainer.appendChild(hideCode);
            hideCode.onclick = function() {
                var codeBlock = this.parentElement.parentElement.lastChild;
                if (this.className === "hideCode") {
                    codeBlock.style.display = "none";
                    this.className = "showCode";
                    this.innerText = show;
                } else {
                    codeBlock.style.display = "block";
                    this.className = "hideCode";
                    this.innerText = hide;
                }
            };

            pre.insertBefore(buttonContainer, pre.firstChild);
        });
    }

    window.addEventListener('load', initCodeTools);
})();