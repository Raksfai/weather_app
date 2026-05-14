const COMPARE_KEY = "compare"
const COMPARE_LIMIT = 5

let compareCharts = []
let compareRows = []
let compareSort = { key: null, direction: "asc" }

function getI18nMessages() {
    const element = document.getElementById("weather-i18n")
    if (!element) return {}

    try {
        return JSON.parse(element.textContent)
    } catch {
        return {}
    }
}

function compareT(key, fallback) {
    return getI18nMessages()[key] || fallback
}

function getCompareList() {
    const raw = localStorage.getItem(COMPARE_KEY)
    if (!raw) return []

    try {
        const cities = JSON.parse(raw)
        if (!Array.isArray(cities)) return []
        return cities.filter(Boolean).slice(0, COMPARE_LIMIT)
    } catch {
        return []
    }
}

function saveCompareList(cities) {
    localStorage.setItem(COMPARE_KEY, JSON.stringify(cities.slice(0, COMPARE_LIMIT)))
}

function renderCompareCount() {
    const compareButton = document.getElementById("compare-open-btn")
    const toggleButton = document.getElementById("compare-toggle-btn")
    const cities = getCompareList()

    if (compareButton) {
        compareButton.textContent = `⚖️ ${compareT("compare", "Compare")} (${cities.length})`
        compareButton.disabled = cities.length < 2
        compareButton.classList.toggle("is-disabled", cities.length < 2)
    }

    if (toggleButton) {
        const currentCity = toggleButton.dataset.city
        const isSelected = cities.includes(currentCity)
        toggleButton.textContent = isSelected
            ? compareT("inCompare", "✓ In compare")
            : compareT("addToCompare", "⚖️ Add to compare")
        toggleButton.classList.toggle("is-active", isSelected)
    }
}

function showCompareMessage(message) {
    const messageElement = document.getElementById("compare-message")
    if (!messageElement) return

    messageElement.textContent = message
    messageElement.hidden = !message
}

function addToCompare(city) {
    const cities = getCompareList()
    if (cities.includes(city)) return cities

    if (cities.length >= COMPARE_LIMIT) {
        openCompareModal(
            compareT("maximumCities", "Maximum 5 cities. Remove one to add another.")
        )
        return cities
    }

    cities.push(city)
    saveCompareList(cities)
    renderCompareCount()
    return cities
}

function removeFromCompare(city) {
    const cities = getCompareList().filter((item) => item !== city)
    saveCompareList(cities)
    renderCompareCount()

    if (document.body.classList.contains("modal-open")) {
        loadCompareData()
    }

    return cities
}

function toggleCompare(city) {
    const cities = getCompareList()
    if (cities.includes(city)) {
        return removeFromCompare(city)
    }
    return addToCompare(city)
}

function openCompareModal(message = "") {
    const modal = document.getElementById("compare-modal")
    if (!modal) return

    modal.classList.add("is-open")
    modal.setAttribute("aria-hidden", "false")
    document.body.classList.add("modal-open")
    showCompareMessage(message)
    loadCompareData(message)
}

function closeCompareModal() {
    const modal = document.getElementById("compare-modal")
    if (!modal) return

    modal.classList.remove("is-open")
    modal.setAttribute("aria-hidden", "true")
    document.body.classList.remove("modal-open")
}

function clearCompareContent() {
    document.getElementById("compare-cards").innerHTML = ""
    document.getElementById("compare-errors").innerHTML = ""
    document.getElementById("compare-table-body").innerHTML = ""
    compareRows = []

    compareCharts.forEach((chart) => chart.destroy())
    compareCharts = []
}

async function loadCompareData(successMessage = "") {
    const cities = getCompareList()
    const subtitle = document.getElementById("compare-subtitle")

    if (subtitle) {
        subtitle.textContent = cities.length
            ? `${cities.length} ${compareT("selected", "selected")}: ${cities.join(", ")}`
            : compareT("selectAtLeastTwo", "Select at least two cities")
    }

    if (cities.length < 2) {
        clearCompareContent()
        showCompareMessage(compareT("addAtLeastTwo", "Add at least two cities to compare."))
        return
    }

    showCompareMessage(compareT("loadingComparison", "Loading comparison..."))

    const params = new URLSearchParams({ cities: cities.join(",") })
    const response = await fetch(`/compare/?${params.toString()}`)
    const payload = await response.json()

    if (!response.ok) {
        clearCompareContent()
        showCompareMessage(
            payload.error || compareT("comparisonUnavailable", "Comparison is unavailable.")
        )
        return
    }

    showCompareMessage(successMessage)
    compareRows = payload.cities || []
    compareSort = { key: null, direction: "asc" }
    renderCompareErrors(payload.errors || [])
    renderCompareCards(compareRows)
    renderCompareTable(compareRows)
    renderCompareChart(compareRows)
}

function renderCompareErrors(errors) {
    const container = document.getElementById("compare-errors")
    container.innerHTML = ""

    errors.forEach((error) => {
        const item = document.createElement("div")
        item.className = "compare-error-item"

        const text = document.createElement("span")
        text.textContent = `${error.city}: ${error.message}`

        const removeButton = document.createElement("button")
        removeButton.type = "button"
        removeButton.className = "btn btn-danger"
        removeButton.textContent = compareT("remove", "Remove")
        removeButton.addEventListener("click", () => removeFromCompare(error.city))

        item.append(text, removeButton)
        container.appendChild(item)
    })
}

function renderCompareCards(cities) {
    const container = document.getElementById("compare-cards")
    container.innerHTML = ""

    cities.forEach((city) => {
        const card = document.createElement("article")
        card.className = `compare-card weather-card-${city.theme}`

        const top = document.createElement("div")
        top.className = "compare-card-top"

        const emoji = document.createElement("span")
        emoji.className = "compare-card-emoji"
        emoji.textContent = city.emoji

        const removeButton = document.createElement("button")
        removeButton.className = "btn btn-danger"
        removeButton.type = "button"
        removeButton.textContent = compareT("remove", "Remove")
        removeButton.addEventListener("click", () => {
            removeFromCompare(city.name)
        })

        const title = document.createElement("h3")
        title.textContent = `${city.name}, ${city.country}`

        const temp = document.createElement("div")
        temp.className = "compare-card-temp"
        temp.textContent = `${Number(city.temp).toFixed(1)}°C`

        const description = document.createElement("p")
        description.textContent = capitalize(city.description)

        const meta = document.createElement("div")
        meta.className = "compare-card-meta"
        const metaItems = [
            `💧 ${city.humidity}%`,
            `🧭 ${city.pressure} hPa`,
            `🌡 ${Number(city.feels_like).toFixed(1)}°C`,
        ]
        metaItems.forEach((value) => {
            const item = document.createElement("span")
            item.textContent = value
            meta.appendChild(item)
        })

        top.append(emoji, removeButton)
        card.append(top, title, temp, description, meta)
        container.appendChild(card)
    })
}

function renderCompareTable(cities) {
    const body = document.getElementById("compare-table-body")
    body.innerHTML = ""

    cities.forEach((city) => {
        const row = document.createElement("tr")

        const values = [
            `${city.name}, ${city.country}`,
            `${Number(city.temp).toFixed(1)}°C`,
            `${city.humidity}%`,
            `${city.pressure} hPa`,
            `${city.emoji} ${capitalize(city.description)}`,
        ]
        values.forEach((value) => {
            const cell = document.createElement("td")
            cell.textContent = value
            row.appendChild(cell)
        })

        const actionCell = document.createElement("td")
        const removeButton = document.createElement("button")
        removeButton.className = "btn btn-danger"
        removeButton.type = "button"
        removeButton.textContent = compareT("remove", "Remove")
        removeButton.addEventListener("click", () => {
            removeFromCompare(city.name)
        })
        actionCell.appendChild(removeButton)
        row.appendChild(actionCell)
        body.appendChild(row)
    })
}

function renderCompareChart(cities) {
    if (!window.Chart) return

    compareCharts.forEach((chart) => chart.destroy())
    compareCharts = []

    const metrics = [
        {
            id: "compare-temp-chart",
            label: compareT("temperature", "Temperature"),
            key: "temp",
            suffix: "°C",
        },
        {
            id: "compare-humidity-chart",
            label: compareT("humidity", "Humidity"),
            key: "humidity",
            suffix: "%",
            max: 100,
        },
        {
            id: "compare-pressure-chart",
            label: compareT("pressure", "Pressure"),
            key: "pressure",
            suffix: " hPa",
        },
    ]

    metrics.forEach((metric) => {
        const canvas = document.getElementById(metric.id)
        if (!canvas) return
        const values = cities.map((city) => city[metric.key])
        const scaleBounds = getReadableBarScale(values, metric.max)

        const chart = new Chart(canvas, {
            type: "bar",
            data: {
                labels: cities.map((city) => city.name),
                datasets: [
                    {
                        label: metric.label,
                        data: values,
                        backgroundColor: cities.map((_city, index) =>
                            getCompareColor(index, 0.62)
                        ),
                        borderColor: cities.map((_city, index) =>
                            getCompareColor(index, 1)
                        ),
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        callbacks: {
                            label(context) {
                                return `${metric.label}: ${context.parsed.y}${metric.suffix}`
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.08)" },
                        ticks: { color: "rgba(255, 255, 255, 0.72)" },
                    },
                    y: {
                        min: scaleBounds.min,
                        max: scaleBounds.max,
                        grid: { color: "rgba(255, 255, 255, 0.08)" },
                        ticks: {
                            color: "rgba(255, 255, 255, 0.72)",
                            callback(value) {
                                return `${value}${metric.suffix}`
                            },
                        },
                    },
                },
            },
        })

        compareCharts.push(chart)
    })
}

function getReadableBarScale(values, fixedMax) {
    const numericValues = values.map(Number).filter((value) => Number.isFinite(value))
    if (!numericValues.length) {
        return { min: undefined, max: fixedMax }
    }

    const minValue = Math.min(...numericValues)
    const maxValue = fixedMax ?? Math.max(...numericValues)
    if (minValue >= maxValue) {
        return { min: undefined, max: fixedMax }
    }

    const minForTenPercentHeight = (minValue - maxValue * 0.1) / 0.9
    return {
        min: Math.floor(minForTenPercentHeight),
        max: fixedMax,
    }
}

function sortCompareRows(key) {
    const direction =
        compareSort.key === key && compareSort.direction === "asc" ? "desc" : "asc"
    compareSort = { key, direction }

    const sortedRows = [...compareRows].sort((left, right) => {
        const leftValue = left[key]
        const rightValue = right[key]

        if (typeof leftValue === "number" && typeof rightValue === "number") {
            return direction === "asc" ? leftValue - rightValue : rightValue - leftValue
        }

        return direction === "asc"
            ? String(leftValue).localeCompare(String(rightValue))
            : String(rightValue).localeCompare(String(leftValue))
    })

    renderCompareTable(sortedRows)
}

function getCompareColor(index, alpha) {
    const colors = [
        `rgba(251, 191, 36, ${alpha})`,
        `rgba(56, 189, 248, ${alpha})`,
        `rgba(167, 139, 250, ${alpha})`,
        `rgba(52, 211, 153, ${alpha})`,
        `rgba(248, 113, 113, ${alpha})`,
    ]
    return colors[index % colors.length]
}

function capitalize(value) {
    if (!value) return ""
    return value.charAt(0).toUpperCase() + value.slice(1)
}

document.addEventListener("DOMContentLoaded", () => {
    const compareButton = document.getElementById("compare-open-btn")
    const closeButton = document.getElementById("compare-close-btn")
    const modal = document.getElementById("compare-modal")
    const toggleButton = document.getElementById("compare-toggle-btn")

    renderCompareCount()

    compareButton?.addEventListener("click", () => {
        if (getCompareList().length >= 2) {
            openCompareModal()
        }
    })

    closeButton?.addEventListener("click", closeCompareModal)

    modal?.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeCompareModal()
        }
    })

    toggleButton?.addEventListener("click", () => {
        toggleCompare(toggleButton.dataset.city)
    })

    document.querySelectorAll(".compare-table th button").forEach((button) => {
        button.addEventListener("click", () => sortCompareRows(button.dataset.sort))
    })

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeCompareModal()
        }
    })
})

window.getCompareList = getCompareList
window.addToCompare = addToCompare
window.removeFromCompare = removeFromCompare
window.toggleCompare = toggleCompare
window.renderCompareCount = renderCompareCount
window.openCompareModal = openCompareModal
window.loadCompareData = loadCompareData
