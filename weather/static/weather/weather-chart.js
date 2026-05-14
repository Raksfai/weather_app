document.addEventListener("DOMContentLoaded", () => {
    function getChartI18nMessages() {
        const element = document.getElementById("weather-i18n")
        if (!element) return {}

        try {
            return JSON.parse(element.textContent)
        } catch {
            return {}
        }
    }

    function chartT(key, fallback) {
        return getChartI18nMessages()[key] || fallback
    }

    const chartElement = document.getElementById("weather-chart")
    const dataElement = document.getElementById("weather-chart-data")
    const selectedElement = document.getElementById("selected-chart-date")

    if (!chartElement || !dataElement || !window.Chart) return

    const chartData = JSON.parse(dataElement.textContent)
    const selectedDate = selectedElement ? JSON.parse(selectedElement.textContent) : null
    const firstDate = selectedDate || Object.keys(chartData)[0]
    const chartTitle = document.getElementById("chart-title")
    const outfitTitle = document.getElementById("outfit-title")
    const outfitSummary = document.getElementById("outfit-summary")
    const outfitList = document.getElementById("outfit-list")
    const weatherThemes = [
        "weather-clear",
        "weather-clouds",
        "weather-rain",
        "weather-snow",
        "weather-thunderstorm",
        "weather-mist",
        "weather-default",
    ]

    function updateOutfitRecommendation(recommendation) {
        if (!recommendation || !outfitTitle || !outfitSummary || !outfitList) return

        outfitTitle.textContent = recommendation.title || ""
        outfitSummary.textContent = recommendation.summary || ""
        outfitList.replaceChildren()

        const items = recommendation.items || []
        items.forEach((item) => {
            const listItem = document.createElement("li")
            listItem.textContent = item
            outfitList.appendChild(listItem)
        })
    }

    const weatherChart = new Chart(chartElement, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: chartT("temperature", "Temperature"),
                    data: [],
                    borderColor: "#fbbf24",
                    backgroundColor: "rgba(251, 191, 36, 0.18)",
                    borderWidth: 3,
                    pointBackgroundColor: "#fef3c7",
                    pointBorderColor: "#f59e0b",
                    pointRadius: 4,
                    tension: 0.36,
                    yAxisID: "temperature",
                },
                {
                    label: chartT("humidity", "Humidity"),
                    data: [],
                    borderColor: "#38bdf8",
                    backgroundColor: "rgba(56, 189, 248, 0.14)",
                    borderWidth: 3,
                    pointBackgroundColor: "#e0f2fe",
                    pointBorderColor: "#0284c7",
                    pointRadius: 4,
                    tension: 0.36,
                    yAxisID: "humidity",
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            responsive: true,
            interaction: {
                intersect: false,
                mode: "index",
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    callbacks: {
                        label(context) {
                            const suffix = context.dataset.yAxisID === "humidity" ? "%" : "°C"
                            return `${context.dataset.label}: ${context.parsed.y}${suffix}`
                        },
                    },
                },
            },
            scales: {
                x: {
                    grid: {
                        color: "rgba(255, 255, 255, 0.08)",
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.7)",
                    },
                },
                temperature: {
                    type: "linear",
                    position: "left",
                    grid: {
                        color: "rgba(255, 255, 255, 0.08)",
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.7)",
                        callback(value) {
                            return `${value}°`
                        },
                    },
                },
                humidity: {
                    type: "linear",
                    position: "right",
                    min: 0,
                    max: 100,
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.7)",
                        callback(value) {
                            return `${value}%`
                        },
                    },
                },
            },
        },
    })

    function updateChart(dateKey) {
        const dayData = chartData[dateKey]
        if (!dayData) return

        weatherChart.data.labels = dayData.points.map((point) => point.label)
        weatherChart.data.datasets[0].data = dayData.points.map((point) => point.temp)
        weatherChart.data.datasets[1].data = dayData.points.map((point) => point.humidity)
        weatherChart.update()

        if (chartTitle) {
            chartTitle.textContent = dayData.title
        }

        updateOutfitRecommendation(dayData.outfit_recommendation)

        document.body.classList.remove(...weatherThemes)
        document.body.classList.add(`weather-${dayData.theme || "default"}`)

        document.querySelectorAll(".forecast-card").forEach((card) => {
            card.classList.toggle("is-active", card.dataset.date === dateKey)
        })
    }

    document.querySelectorAll(".forecast-card").forEach((card) => {
        card.addEventListener("click", () => updateChart(card.dataset.date))
    })

    updateChart(firstDate)
})
