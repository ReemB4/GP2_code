function SelectTag(e, t = { shadow: !1, rounded: !0 }) {
    var l = null, n = null, a = null, d = null, s = null, o = null, i = null, r = null, c = null, u = null, v = null, p = null, h = t.tagColor || {};

    h.textColor = h.textColor || "#FF5D29";
    h.borderColor = h.borderColor || "#FF5D29";
    h.bgColor = h.bgColor || "#FFE9E2";

    var m = new DOMParser;

    function g(e, t, l = !1) {
        const n = document.createElement("li");
        n.innerHTML = "<input type='checkbox' style='margin:0 0.5em 0 0' class='input_checkbox'>";
        n.innerHTML += e.label;
        n.dataset.value = e.value;
        const a = n.firstChild;
        a.dataset.value = e.value;
        if (t && e.label.toLowerCase().includes(t.toLowerCase())) p.appendChild(n);
        else if (!t) p.appendChild(n);
        if (l) {
            n.style.backgroundColor = h.bgColor;
            a.checked = !0;
        }
    }

    function f(e = null) {
        p.innerHTML = "";
        for (var t of n) {
            if (t.selected) {
                C(t);
                g(t, e, !0);
            } else {
                g(t, e);
            }
        }
    }

    function C(e) {
        // Clear existing selected items before adding the new one
        i.innerHTML = "";
        const t = document.createElement("div");
        t.classList.add("item-container");
        t.style.color = h.textColor || "#2c7a7b";
        t.style.borderColor = h.borderColor || "#81e6d9";
        t.style.background = h.bgColor || "#e6fffa";
        const l = document.createElement("div");
        l.classList.add("item-label");
        l.style.color = h.textColor || "#2c7a7b";
        l.innerHTML = e.label;
        l.dataset.value = e.value;
        const a = m.parseFromString('<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="item-close-svg">\n                <line x1="18" y1="6" x2="6" y2="18"></line>\n                <line x1="6" y1="6" x2="18" y2="18"></line>\n            </svg>', "image/svg+xml").documentElement;
        a.addEventListener("click", (t => {
            n.find((t => t.value == e.value)).selected = !1;
            f();
            E();
        }));
        t.appendChild(l);
        t.appendChild(a);
        i.append(t);
    }

    function L() {
        for (var e of p.children) {
            e.addEventListener("click", (e => {
                // Deselect all other options first
                n.forEach(item => item.selected = !1);
                // Select the clicked item
                const selectedOption = n.find(t => t.value == e.target.dataset.value);
                if (selectedOption) {
                    selectedOption.selected = !0;
                    c.value = null;
                    f();
                    E();
                }
            }));
        }
    }

    function b(e) {
        return Array.from(i.children).some(t => !t.classList.contains("input-body") && t.firstChild.dataset.value == e);
    }

    function w(e) {
        for (var t of i.children) {
            if (!t.classList.contains("input-body") && t.firstChild.dataset.value == e) {
                i.removeChild(t);
            }
        }
    }

    function E(e = !0) {
        selected_values = [];
        for (var a = 0; a < n.length; a++) {
            l.options[a].selected = n[a].selected;
            if (n[a].selected) selected_values.push({ label: n[a].label, value: n[a].value });
        }
        if (e && t.hasOwnProperty("onChange")) t.onChange(selected_values);
    }

    l = document.getElementById(e);
    (function () {
        n = [...l.options].map((e => ({ value: e.value, label: e.label, selected: e.selected })));
        l.classList.add("hidden");
        (a = document.createElement("div")).classList.add("mult-select-tag");
        (d = document.createElement("div")).classList.add("wrapper");
        (o = document.createElement("div")).classList.add("body");
        if (t.shadow) o.classList.add("shadow");
        if (t.rounded) o.classList.add("rounded");
        (i = document.createElement("div")).classList.add("input-container");
        (c = document.createElement("input")).classList.add("input");
        c.placeholder = `${t.placeholder || "Search..."}`;
        (r = document.createElement("inputBody")).classList.add("input-body");
        r.append(c);
        o.append(i);
        (s = document.createElement("div")).classList.add("btn-container");
        (u = document.createElement("button")).type = "button";
        s.append(u);
        const e = m.parseFromString('<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n                <polyline points="18 15 12 21 6 15"></polyline>\n            </svg>', "image/svg+xml").documentElement;
        u.append(e);
        o.append(s);
        d.append(o);
        (v = document.createElement("div")).classList.add("drawer", "hidden");
        if (t.shadow) v.classList.add("shadow");
        if (t.rounded) v.classList.add("rounded");
        v.append(r);
        p = document.createElement("ul");
        v.appendChild(p);
        a.appendChild(d);
        a.appendChild(v);
        if (l.nextSibling) l.parentNode.insertBefore(a, l.nextSibling);
        else l.parentNode.appendChild(a);
    })();

    f();
    L();
    E(!1);

    u.addEventListener("click", (() => {
        if (v.classList.contains("hidden")) {
            f();
            L();
            v.classList.remove("hidden");
            c.focus();
        } else v.classList.add("hidden");
    }));
    c.addEventListener("keyup", (e => {
        f(e.target.value);
        L();
    }));
    c.addEventListener("keydown", (e => {
        if ("Backspace" === e.key && !e.target.value && i.childElementCount > 1) {
            const e = o.children[i.childElementCount - 2].firstChild;
            n.find((t => t.value == e.dataset.value)).selected = !1;
            w(e.dataset.value);
            E();
        }
    }));
    window.addEventListener("click", (e => {
        if (!a.contains(e.target)) v.classList.add("hidden");
    }));
}
