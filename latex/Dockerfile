FROM debian:trixie-slim

# ttf-mscorefonts-installer (Times New Roman, Arial, Courier New) lives in contrib and asks to
# accept the Microsoft EULA interactively; pre-seed the answer so the build is non-interactive.
RUN sed -i 's/^Components: main$/Components: main contrib/' /etc/apt/sources.list.d/debian.sources \
    && echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        fontconfig \
        fonts-texgyre-math \
        ttf-mscorefonts-installer \
        texlive-xetex \
        texlive-fonts-recommended \
        texlive-lang-cyrillic \
        texlive-latex-extra \
        texlive-bibtex-extra \
        biber \
        latexmk \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
