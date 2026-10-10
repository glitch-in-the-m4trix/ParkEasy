$("document").ready(() => {
    // Active Switching
    const currentPath = window.location.pathname;
    const navLinks = $(".nav-item .nav-link");

    navLinks.each(function () {
        const href = $(this).attr("href");

        if (href == currentPath) {
            $(this).closest(".nav-item").addClass("active");
        }
    });


    // Notification Display
    var $messages = $(".message");

    if ($messages.length) {
        const messageMap = {
            success: { type: "success", icon: "check_circle" },
            info: { type: "info", icon: "info" },
            warning: { type: "warning", icon: "warning" },
            error: { type: "danger", icon: "error" }
        };

        $messages.each((_idx, message) => {
            let messageText = $(message).data("message");
            let messageType = $(message).data("type");

            $.notify({
                icon: messageMap[messageType].icon,
                message: messageText
            }, {
                type: messageMap[messageType].type,
                timer: 3000,
                placement: {
                    from: "top",
                    align: "right"
                },
            });
        });
    }

    // District Filter
    const stateSelect = $("#id_state");
    const districtSelect = $("#id_district");

    stateSelect.change(() => {
        const selectedState = stateSelect.val();

        districtSelect.append('<option value="">Select District</option>');
        if (!selectedState) return;

        $.ajax({
            url: "/filter-districts/",
            method: "GET",
            data: {
                state: selectedState
            },
            success: (response) => {
                districtSelect.empty();
                response.districts.forEach((district) => {
                    const option = $(`<option value="${district.id}">${district.name}</option>`);
                    districtSelect.append(option);
                });
            },
            error: (xhr, status, error) => {
                console.error("Error fetching districts:", error);
            }
        });
    });


    // Map Initialization
    const mapContainer = document.getElementById("parking-map");
    if (mapContainer) {
        const map = L.map("parking-map").setView(
            [8.4901, 76.9535], 15
        );

        // Load OpenStreetMap tiles
        L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {
            attribution: "Tiles &copy; Esri"
        }).addTo(map);

        const mapContainer = map.getContainer();

        mapContainer.addEventListener("wheel", function (event) {
            event.preventDefault();
        }, { passive: false });

        let marker;

        map.on("click", function (event) {
            const latitude = event.latlng.lat.toFixed(6);
            const longitude = event.latlng.lng.toFixed(6);

            document.getElementById("id_latitude").value = latitude;
            document.getElementById("id_longitude").value = longitude;

            if (marker) {
                marker.setLatLng(event.latlng);
            } else {
                marker = L.marker(event.latlng).addTo(map);
            }

            // marker.bindPopup(
            //     `Latitude: ${latitude}<br>
            //      Longitude: ${longitude}`
            // ).openPopup();
        });
    }


    // const nearbyParking = document.getElementById("nearby-parking");

    // if (nearbyParking) {
    //     nearbyParking.addEventListener("click", (event) => {
    //         event.preventDefault();
    //         url = event.currentTarget.href;

    //         navigator.geolocation.getCurrentPosition(
    //             function (position) {
    //                 const latitude = position.coords.latitude;
    //                 const longitude = position.coords.longitude;

    //                 window.location.href = `${url}${latitude}/${longitude}/`;
    //             },
    //             function (error) {
    //                 console.log("Location error:", error);
    //             }
    //         );
    //     });
    // }


    // Book Slot
    const slots = document.querySelectorAll(".slot-unavailable");

    if (slots) {
        slots.forEach(slot => {
            slot.addEventListener("click", (event) => {
                event.preventDefault();

                $.notify({
                    icon: "error",
                    message: "Slot is unavailable"
                }, {
                    type: "danger",
                    timer: 3000,
                    placement: {
                        from: "top",
                        align: "right"
                    },
                });
            });
        });
    }


    // Rating
    const stars = document.querySelectorAll("#star-rating .bi");
    const ratingInput = document.getElementById("id_rating");

    if (stars) {
        stars.forEach(star => {
            star.addEventListener("click", () => {
                const rating = Number(star.getAttribute("data-rating"));

                ratingInput.value = rating;

                stars.forEach(s => {
                    const starRating = Number(s.getAttribute("data-rating"));

                    if (starRating <= rating) {
                        s.classList.remove("bi-star");
                        s.classList.add("bi-star-fill");
                    } else {
                        s.classList.remove("bi-star-fill");
                        s.classList.add("bi-star");
                    }
                });
            });
        });
    }
});