let fleetDomainsLoading = false;

function fleetDomainAccessible(domain) {
    if (!domain) return false;
    if (currentUser?.is_admin) return true;
    return (
        userHasPermission("dashboard", domain)
        || userHasPermission("dns", domain)
        || userHasPermission("emails", domain)
    );
}

function renderFleetHealthPlaceholder(message) {
    const tbody = document.getElementById("fleet-health-tbody");
    if (!tbody) return;
    setTrustedHtml(tbody, tablePlaceholderRowHtml(4, message));
}

function renderFleetHealthRows(rows) {
    const tbody = document.getElementById("fleet-health-tbody");
    const card = document.getElementById("fleet-health-card");
    if (!tbody) return;

    if (!rows.length) {
        renderFleetHealthPlaceholder("No domains to show.");
        return;
    }

    setTrustedHtml(tbody, "");
    rows.forEach((row) => {
        const tr = document.createElement("tr");
        tr.dataset.domain = row.domain;
        tr.style.cursor = "pointer";
        tr.title = `Switch to ${row.domain}`;
        tr.innerHTML = `
            <td><strong>${escapeHtml(row.domain)}</strong></td>
            <td>${row.mailHtml}</td>
            <td>${row.dnsHtml}</td>
            <td style="text-align: right;">${escapeHtml(row.mailboxCount)}</td>
        `;
        tbody.appendChild(tr);
    });
    if (card) card.dataset.loaded = "true";
}

async function loadFleetDomainRow(domain, { force = false } = {}) {
    const canLoadMail = userHasPermission("emails", domain) || userHasPermission("dashboard", domain);
    const snapshot = await ensureDomainRowStatus(domain, {
        force,
        includeMailboxes: canLoadMail,
    });
    const fallback = `<span style="color: var(--color-muted); font-size: 0.85rem;">—</span>`;
    return {
        domain,
        mailHtml: snapshot?.mailHtml || fallback,
        dnsHtml: snapshot?.dnsHtml || fallback,
        mailboxCount: snapshot?.mailboxCount != null ? String(snapshot.mailboxCount) : "—",
    };
}

async function loadFleetHealth({ force = false } = {}) {
    const card = document.getElementById("fleet-health-card");
    if (!card || fleetDomainsLoading) {
        return;
    }

    fleetDomainsLoading = true;
    const firstLoad = card.dataset.loaded !== "true";
    card.style.display = "";
    if (firstLoad) {
        renderFleetHealthPlaceholder("Loading fleet status...");
    }

    try {
        const result = await cachedFetch("/api/domains", { force });
        const domains = (result?.success && result.data ? result.data : [])
            .filter((domain) => fleetDomainAccessible(domain));

        if (domains.length < 2) {
            card.style.display = "none";
            return;
        }

        if (result?.success && result.data) {
            domainsListAll = result.data;
        }

        setElementRefreshing(card, true);
        const rows = await window.Mxm.utils.mapWithConcurrency(
            domains,
            5,
            (domain) => loadFleetDomainRow(domain, { force }),
        );
        rows.sort((a, b) => a.domain.localeCompare(b.domain));
        renderFleetHealthRows(rows);
    } catch (err) {
        console.warn("Fleet health load failed:", err);
        if (firstLoad) {
            renderFleetHealthPlaceholder("Could not load fleet status.");
        }
    } finally {
        setElementRefreshing(card, false);
        fleetDomainsLoading = false;
    }
}

function initFleetHealthTable() {
    const tbody = document.getElementById("fleet-health-tbody");
    if (!tbody || tbody.dataset.clickInit === "true") {
        return;
    }
    tbody.dataset.clickInit = "true";
    tbody.addEventListener("click", (event) => {
        const row = event.target.closest("tr[data-domain]");
        if (!row?.dataset.domain) return;
        const domain = row.dataset.domain;
        const select = document.getElementById("global-domain-select");
        if (select) {
            select.value = domain;
            select.dispatchEvent(new Event("change"));
        }
    });
}

document.getElementById("btn-refresh-fleet-health")?.addEventListener("click", async () => {
    const btn = document.getElementById("btn-refresh-fleet-health");
    if (btn) {
        btn.disabled = true;
        setTrustedHtml(btn, btnLabel("arrow-clockwise", "Refreshing...", true));
    }
    try {
        await loadFleetHealth({ force: true });
        const card = document.getElementById("fleet-health-card");
        if (card?.style.display === "none") {
            showAlert("info", "Fleet overview appears when you have two or more domains.");
        } else {
            showAlert("success", "Fleet status refreshed.");
        }
    } catch (err) {
        showAlert("error", err.message);
    } finally {
        if (btn) {
            btn.disabled = false;
            setTrustedHtml(btn, btnLabel("arrow-clockwise", "Refresh fleet"));
        }
    }
});

initFleetHealthTable();
