function getFavoriteI18nMessages() {
    const element = document.getElementById("weather-i18n")
    if (!element) return {}

    try {
        return JSON.parse(element.textContent)
    } catch {
        return {}
    }
}

function favoriteT(key, fallback) {
    return getFavoriteI18nMessages()[key] || fallback
}

function addFavorite(city) {
    let favorites = getFavorites()
    if (favorites.includes(city)) return
    favorites.push(city)
    localStorage.setItem("favorites", JSON.stringify(favorites));
    renderFavorites()
}

function removeFavorite(city) {
    let favorites = getFavorites()
    favorites = favorites.filter(fav => fav !== city)
    localStorage.setItem("favorites", JSON.stringify(favorites));
    renderFavorites()
}

function getFavorites() {
    const raw = localStorage.getItem("favorites")
    if (!raw) return []
    return JSON.parse(raw)
}

function renderFavorites() {
    const favorites = getFavorites()
    const container = document.getElementById("favorites-list")
    container.innerHTML = ""
    if (favorites.length === 0) {
        const empty = document.createElement("div")
        empty.classList.add("favorite-item")
        const text = document.createElement("p")
        text.textContent = favoriteT("noFavorites", "No favorites yet.")
        empty.appendChild(text)
        container.appendChild(empty)
        return
    }
    favorites.forEach(city => {
        const div = document.createElement("div")
        div.classList.add("favorite-item")
        const link = document.createElement("a")
        link.href = `/?city=${encodeURIComponent(city)}`
        link.textContent = city
        const button = document.createElement("button")
        button.className = "btn btn-danger"
        button.type = "button"
        button.textContent = favoriteT("remove", "Remove")
        button.addEventListener("click", () => removeFavorite(city))
        div.append(link, button)
        container.appendChild(div)
    })
}

document.getElementById("favorites-btn").addEventListener("click", function() {
    const list = document.getElementById("favorites-list")
    if (list.style.display === "block") {
        list.style.display = "none"
    } else {
        list.style.display = "block"
    }
})

document.addEventListener("DOMContentLoaded", renderFavorites)
