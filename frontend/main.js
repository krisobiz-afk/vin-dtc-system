// frontend/main.js

$(document).ready(function() {
  const API = "http://127.0.0.1:8000";
  let currentFilters = {};

  // Зареждаме автомобили, като подаваме филтрите директно към бекенда
  function loadVehicles(filters = {}) {
    const params = new URLSearchParams(filters);
    const url = `${API}/vehicles/?${params.toString()}`;

    console.log("Loading from URL:", url);
    $.getJSON(url)
      .done(function(data) {
        const $tbody = $("#vehicles-table tbody").empty();
        data.forEach((v, i) => {
          $tbody.append(`
            <tr class="text-center border-b">
              <td class="px-2 py-2 border">${v.vin}</td>
              <td class="px-2 py-2 border">${v.label}</td>
              <td class="px-2 py-2 border">${v.comment}</td>
              <td class="px-2 py-2 border space-x-2">
                <button data-vin="${v.vin}" class="details-btn bg-blue-600 text-white px-1 py-1 rounded hover:bg-blue-700">Виж детайли</button>
                <button data-vin="${v.vin}" class="delete-btn bg-red-600 text-white px-1 py-1 rounded hover:bg-red-700">Изтрий</button>
              </td>
            </tr>
          `);
        });
      })
      .fail(function(err) {
        console.error("Fetch vehicles error:", err);
      });
  }

  // Детайли
  $(document).on("click", ".details-btn", function() {
    const vin = $(this).data("vin");
    fetch(`${API}/vehicles/${vin}`)
      .then(res => res.json())
      .then(d => {
        $("#details-vin").text(vin);
        $("#modules-list").empty();
        d.modules.forEach(m => {
          $("#modules-list").append(`<li><strong>${m.name}</strong> — ${m.part_number}</li>`);
        });
        $("#errors-list").empty();
        d.errors.forEach(e => {
          $("#errors-list").append(`<li><strong>${e.code}</strong>: ${e.description}</li>`);
        });
        $("#details").removeClass("hidden");
      })
      .catch(err => console.error("Fetch details error:", err));
  });

  // Изтриване
  $(document).on("click", ".delete-btn", function() {
    const vin = $(this).data("vin");
    if (!confirm(`Сигурни ли сте? Изтриване на ${vin}`)) return;
    fetch(`${API}/vehicles/${vin}`, { method: "DELETE" })
      .then(() => {
        loadVehicles(currentFilters);
        $("#details").addClass("hidden");
      })
      .catch(err => console.error("Delete error:", err));
  });

  // Търсене
  $("#search-btn").click(function() {
    currentFilters = {
      vin: $("#search-vin").val().trim(),
      label: $("#search-label").val().trim(),
      dtc: $("#search-dtc").val().trim()
    };
    loadVehicles(currentFilters);
    $("#details").addClass("hidden");
  });

  // Изчистване
  $("#clear-btn").click(function() {
    $("#search-vin, #search-label, #search-dtc").val("");
    currentFilters = {};
    loadVehicles();
    $("#details").addClass("hidden");
  });

  // Качване
  $("#upload-form").submit(function(e) {
    e.preventDefault();
    const modules = $("#modules_file")[0].files[0];
    const dtc     = $("#dtc_file")[0].files[0] || null;
    const label   = $("#label").val().trim();
    const comment = $("#comment").val().trim();

    if (!modules) {
      $("#upload-status").text("Моля, изберете конфигурационен файл.");
      return;
    }

    const form = new FormData();
    form.append("modules_file", modules);
    if (dtc) form.append("dtc_file", dtc);
    form.append("label", label);
    form.append("comment", comment);

    fetch(`${API}/upload/combined/`, { method: "POST", body: form })
      .then(res => res.json())
      .then(data => {
        if (data.status === "ok") {
          $("#upload-status").text("Качено: " + data.vin);
          $("#upload-form")[0].reset();
          loadVehicles(currentFilters);
        } else {
          $("#upload-status").text("Грешка при качване.");
        }
      })
      .catch(err => {
        console.error("Upload error:", err);
        $("#upload-status").text("Сървърна грешка.");
      });
  });

  // Начално зареждане (без филтри)
  loadVehicles();
});
