# Configuration file for the Sphinx documentation builder.
#

import os
import sys
sys.path.insert(0, os.path.abspath('../'))


project = 'TSADmetrics'
copyright = '2025, Pedro Rafael Velasco Priego'
author = 'Pedro Rafael Velasco Priego'
release = 'MIT'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = ['sphinx.ext.duration', 'sphinx.ext.doctest', 'sphinx.ext.autodoc',]



templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'furo'
html_static_path = ['_static']
html_theme_options = {
    #"sidebar_hide_name": True,
    "light_css_variables": {
        "color-brand-primary": "#2e5c7d",
        "color-brand-content": "#2e5c7d",
        "codebgcolor": "red",
        "codetextcolor": "red",
    },
    "dark_css_variables": {
        "color-brand-primary": "#6998b4",
        "color-brand-content": "#6998b4",
        "codebgcolor": "green",
        "codetextcolor": "green",
    },
    "navigation_with_keys": True

}
html_baseurl = ''

html_css_files = [
    'css/custom.css',
]

epub_show_urls = 'footnote'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output




### -- LaTeX options -------------------------------------------------

# comando para compilar: make latexpdf LATEXMKOPTS="-xelatex"

latex_elements = {
    'maxlistdepth': '10',  # Aumenta el límite de anidamiento
    'papersize': 'a4paper',
    'pointsize': '10pt',
    'maketitle': r'''
\makeatletter
\begin{titlepage}
\noindent\rule{\textwidth}{1pt}\\[3cm]
\begin{center}
{\Huge\sffamily\bfseries TSADmetrics API Reference}\\[1.5cm]
{\Large\sffamily Time Series Anomaly Detection Metrics}\\[3cm]
\begin{minipage}{0.8\textwidth}
\centering
{\large\sffamily
\begin{tabular}{l@{\hspace{1cm}}l}
\textbf{Autor:}      & Pedro Rafael Velasco Priego \\
\textbf{Directores:} & Dra. Amelia Zafra Gómez \\
                     & Dr. Sebastián Ventura Soto \\
\end{tabular}
}
\end{minipage}\\[5cm]
{\large\sffamily \@date}\\
{\large\sffamily \copyright\ 2025 Pedro Rafael Velasco Priego}
\end{center}
\noindent\rule{\textwidth}{1pt}
\end{titlepage}
\makeatother
''',
}