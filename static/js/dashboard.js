(function () {
    'use strict';

    var canvas = document.getElementById('monthlyEvolutionChart');
    if (!canvas) return;

    var url = canvas.dataset.url;

    function formatBRL(value) {
        return 'R$ ' + value.toLocaleString('pt-BR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    fetch(url, { credentials: 'same-origin' })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            var labels   = data.map(function (d) { return d.month; });
            var incomes  = data.map(function (d) { return d.income; });
            var expenses = data.map(function (d) { return d.expense; });
            var balances = data.map(function (d) { return d.balance; });

            new Chart(canvas, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Receitas',
                            data: incomes,
                            borderColor: '#22c55e',
                            backgroundColor: 'rgba(34, 197, 94, 0.08)',
                            pointBackgroundColor: '#22c55e',
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            tension: 0.4,
                            fill: true,
                            borderWidth: 2
                        },
                        {
                            label: 'Despesas',
                            data: expenses,
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.08)',
                            pointBackgroundColor: '#ef4444',
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            tension: 0.4,
                            fill: true,
                            borderWidth: 2
                        },
                        {
                            label: 'Saldo',
                            data: balances,
                            borderColor: '#a78bfa',
                            backgroundColor: 'rgba(167, 139, 250, 0.08)',
                            pointBackgroundColor: '#a78bfa',
                            pointRadius: 4,
                            pointHoverRadius: 6,
                            tension: 0.4,
                            fill: true,
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: '#525252',
                                font: { size: 12, family: 'Inter, sans-serif' },
                                boxWidth: 12,
                                boxHeight: 12,
                                padding: 20
                            }
                        },
                        tooltip: {
                            backgroundColor: '#111111',
                            titleColor: '#f5f5f5',
                            titleFont: { family: 'Inter, sans-serif', size: 13, weight: 'bold' },
                            bodyColor: '#a3a3a3',
                            bodyFont: { family: '"JetBrains Mono", monospace', size: 12 },
                            borderColor: '#262626',
                            borderWidth: 1,
                            padding: 14,
                            cornerRadius: 8,
                            callbacks: {
                                label: function (ctx) {
                                    return ' ' + ctx.dataset.label + ': ' + formatBRL(ctx.parsed.y);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#525252', font: { size: 12 } },
                            grid: { color: 'rgba(38, 38, 38, 0.8)' },
                            border: { color: 'rgba(38, 38, 38, 0.8)' }
                        },
                        y: {
                            ticks: {
                                color: '#525252',
                                font: { size: 11 },
                                callback: function (value) { return formatBRL(value); }
                            },
                            grid: { color: 'rgba(38, 38, 38, 0.8)' },
                            border: { color: 'rgba(38, 38, 38, 0.8)' }
                        }
                    }
                }
            });
        })
        .catch(function (err) {
            console.error('Erro ao carregar evolução mensal:', err);
        });
})();
