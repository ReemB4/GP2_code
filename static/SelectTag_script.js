function SelectTag(e, t = { shadow: !1, rounded: !0 }) {
    var l = null, n = null, a = null, d = null, s = null, o = null, i = null, r = null, c = null, u = null, v = null, p = null, h = t.tagColor || {};

    h.textColor = h.textColor || "#FF5D29";
    h.borderColor = h.borderColor || "#FF5D29";
    h.bgColor = h.bgColor || "#FFE9E2";

    var m = new DOMParser;

    // Generates an option list item (li)
    function g(e, t, l = !1) {
        const n = document.createElement("li");
        n.innerHTML = "<input type='checkbox' style='margin:0 0.5em 0 0' class='input_checkbox'>";
        n.innerHTML += e.label;
        n.dataset.value = e.value;
        const a = n.firstChild;
        a.dataset.value = e.value;

        if (l) {
            n.style.backgroundColor = h.bgColor;
            a.checked = true;
        } else {
            a.checked = false;
        }
        t ? p.appendChild(n) : p.appendChild(n);
    }

    // Refreshes the list of options and keeps only the last selected one
    function f(e = null) {
        p.innerHTML = ""; // Clear the options
        let selectedOption = n.find(opt => opt.selected);
        n.forEach(opt => opt.selected = false); // Deselect all
        if (selectedOption) selectedOption.selected = true; // Keep only the last selected

        for (let t of n) {
            g(t, e, t.selected); // Render options with the correct selection state
        }
        if (selectedOption) C(selectedOption); // Show the last selected tag
    }

    // Creates the selected tag with close button
    function C(e) {
        // Remove all other tags before adding the new one
        i.innerHTML = "";

        const t = document.createElement("div");
        t.classList.add("item-container");
        t.style.color = h.textColor;
        t.style.borderColor = h.borderColor;
        t.style.background = h.bgColor;

        const l = document.createElement("div");
        l.classList.add("item-label");
        l.style.color = h.textColor;
        l.innerHTML = e.label;
        l.dataset.value = e.value;

        const a = m.parseFromString(`
            <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" 
            viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" 
            stroke-linejoin="round" class="item-close-svg">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        `, "image/svg+xml").documentElement;

        a.addEventListener("click", () => {
            e.selected = false; // Deselect the option
            i.innerHTML = ""; // Clear the tag
            f(); // Refresh the list
            E(); // Trigger onChange
        });

        t.appendChild(l);
        t.appendChild(a);
        i.appendChild(t);
    }

    // Adds click listeners to options to ensure only the last one remains selected
    function L() {
        for (let e of p.children) {
            e.addEventListener("click", () => {
                n.forEach(opt => opt.selected = false); // Deselect all
                const selectedOption = n.find(t => t.value == e.dataset.value);
                selectedOption.selected = true; // Select the clicked option

                f(); // Refresh the list
                E(); // Trigger onChange
            });
        }
    }

    // Checks if a tag already exists (not needed now since only one is allowed)
    function b(value) {
        return Array.from(i.children).some(t => t.firstChild.dataset.value == value);
    }

    // Updates the native select and triggers onChange if needed
    function E(trigger = true) {
        const selectedValues = [];
        n.forEach((option, index) => {
            l.options[index].selected = option.selected;
            if (option.selected) selectedValues.push({ label: option.label, value: option.value });
        });

        if (trigger && t.onChange) t.onChange(selectedValues);
    }

    // Initialize the component
    l = document.getElementById(e);
    n = Array.from(l.options).map(opt => ({ value: opt.value, label: opt.label, selected: opt.selected }));
    l.classList.add("hidden");

    a = document.createElement("div");
    a.classList.add("mult-select-tag");

    d = document.createElement("div");
    d.classList.add("wrapper");

    o = document.createElement("div");
    o.classList.add("body");
    if (t.shadow) o.classList.add("shadow");
    if (t.rounded) o.classList.add("rounded");

    i = document.createElement("div");
    i.classList.add("input-container");

    c = document.createElement("input");
    c.classList.add("input");
    c.placeholder = t.placeholder || "Search...";

    r = document.createElement("inputBody");
    r.classList.add("input-body");
    r.appendChild(c);

    o.appendChild(i);

    s = document.createElement("div");
    s.classList.add("btn-container");

    u = document.createElement("button");
    u.type = "button";
    s.appendChild(u);

    const svg = m.parseFromString(`
        <svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="none" 
        viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" 
        stroke-linejoin="round">
            <polyline points="18 15 12 21 6 15"></polyline>
        </svg>
    `, "image/svg+xml").documentElement;

    u.appendChild(svg);
    o.appendChild(s);
    d.appendChild(o);

    v = document.createElement("div");
    v.classList.add("drawer", "hidden");
    if (t.shadow) v.classList.add("shadow");
    if (t.rounded) v.classList.add("rounded");

    v.appendChild(r);

    p = document.createElement("ul");
    v.appendChild(p);

    a.appendChild(d);
    a.appendChild(v);
    l.parentNode.insertBefore(a, l.nextSibling);

    f(); // Initial render
    L(); // Attach listeners
    E(false); // Sync initial values

    // Toggle dropdown visibility
    u.addEventListener("click", () => {
        v.classList.toggle("hidden");
        if (!v.classList.contains("hidden")) {
            f();
            L();
            c.focus();
        }
    });

    // Search input listener
    c.addEventListener("keyup", e => {
        f(e.target.value);
        L();
    });

    c.addEventListener("keyup",(e=>{f(e.target.value),L()})),c.addEventListener("keydown",(e=>{if("Backspace"===e.key&&!e.target.value&&i.childElementCount>1){const e=o.children[i.childElementCount-2].firstChild;
        n.find((t=>t.value==e.dataset.value)).selected=!1,w(e.dataset.value),E()}}))

    // Hide dropdown on outside click
    window.addEventListener("click", e => {
        if (!a.contains(e.target)) v.classList.add("hidden");
    });

}
