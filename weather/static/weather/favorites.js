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
        container.innerHTML = "<p>No favorites yet.</p>"
        return
    }
    favorites.forEach(city => {
        const div = document.createElement("div")
        div.classList.add("favorite-item")
        div.innerHTML = `
            <a href="/?city=${city}">${city}</a>
            <button class="btn btn-danger" onclick="removeFavorite('${city}')">Remove</button>
        `
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