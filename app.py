/* Streamlit mobile badge fix */

[data-testid="stStatusWidget"] {
    display: none !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stBadge"] {
    display: none !important;
}

[data-testid="stAppToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stBottom"] {
    display: none !important;
}

/* Hide all floating streamlit badges */
div[class*="viewerBadge_container"] {
    display: none !important;
}

div[class*="viewerBadge"] {
    display: none !important;
}

button[class*="viewerBadge"] {
    display: none !important;
}

a[class*="viewerBadge"] {
    display: none !important;
}

a[href*="streamlit.io"] {
    display: none !important;
}

iframe {
    display: none !important;
}
