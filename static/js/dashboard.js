const table = document.getElementById("table")
const form = document.getElementById("form")
const filter = document.getElementById("month-filter")

let chart

async function loadTransactions() {
  const month = filter.value
  const response = await fetch(`/transactions?month=${month}`)
  const data = await response.json()

  table.innerHTML = ""

  let income = 0
  let expense = 0

  data.forEach((t) => {
    const row = document.createElement("tr")

    row.innerHTML = `
      <td>${t.description}</td>
      <td class="${t.type === "income" ? "income" : "expense"}">R$ ${Number(
      t.amount
    ).toFixed(2)}</td>
      <td>${t.type === "income" ? "Receita" : "Despesa"}</td>
      <td>${t.date}</td>
      <td><button class="delete-btn" onclick="deleteTransaction(${t.id})">X</button></td>
    `

    table.appendChild(row)

    if (t.type === "income") {
      income += Number(t.amount)
    } else {
      expense += Number(t.amount)
    }
  })

  renderChart(income, expense)
}

form.addEventListener("submit", async (e) => {
  e.preventDefault()

  const description = document.getElementById("description").value
  const amount = document.getElementById("amount").value
  const type = document.getElementById("type").value

  await fetch("/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description, amount, type }),
  })

  form.reset()
  loadTransactions()
})

async function deleteTransaction(id) {
  await fetch(`/transactions/${id}`, {
    method: "DELETE",
  })

  loadTransactions()
}

function renderChart(income, expense) {
  const ctx = document.getElementById("chart")

  if (chart) {
    chart.destroy()
  }

  chart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: ["Receita", "Despesa"],
      datasets: [
        {
          data: [income, expense],
          backgroundColor: ["#22c55e", "#ef4444"],
        },
      ],
    },
  })
}

filter.addEventListener("change", loadTransactions)

loadTransactions()
