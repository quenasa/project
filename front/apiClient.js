(function (global) {
  'use strict'

  const base = window.API_BASE || '/api'

  function checkRequiredLatLon(lat, lon) {
    if (lat === undefined || lon === undefined) {
      throw new Error('lat and lon parameters are required')
    }
    const nlat = Number(lat)
    const nlon = Number(lon)
    if (Number.isNaN(nlat) || Number.isNaN(nlon)) throw new Error('lat and lon must be numbers')
    return { lat: nlat, lon: nlon }
  }

  async function safeFetch(url) {
    const res = await fetch(url)
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      const err = new Error('Request failed: ' + res.status + ' ' + res.statusText)
      err.status = res.status
      err.body = text
      throw err
    }
    return res.json()
  }

  async function getReports() {
    const url = base + '/reports'
    return safeFetch(url)
  }

  async function getSocioeconomic(lat, lon) {
    checkRequiredLatLon(lat, lon)
    const url = new URL(base + '/socioeconomic', window.location.href)
    url.searchParams.set('lat', lat)
    url.searchParams.set('lon', lon)
    return safeFetch(url.toString())
  }

  async function getEnvironmental(lat, lon, country) {
    checkRequiredLatLon(lat, lon)
    const url = new URL(base + '/environmental', window.location.href)
    url.searchParams.set('lat', lat)
    url.searchParams.set('lon', lon)
    if (country) url.searchParams.set('country', country)
    return safeFetch(url.toString())
  }

  async function getVulnerability(lat, lon, country) {
    checkRequiredLatLon(lat, lon)
    const url = new URL(base + '/vulnerability', window.location.href)
    url.searchParams.set('lat', lat)
    url.searchParams.set('lon', lon)
    if (country) url.searchParams.set('country', country)
    return safeFetch(url.toString())
  }

  // Expose a simple client
  const apiClient = {
    getReports,
    getSocioeconomic,
    getEnvironmental,
    getVulnerability,
  }

  // Attach to window for use from non-module scripts
  global.apiClient = apiClient
  // also export for modules
  if (typeof module !== 'undefined' && module.exports) module.exports = apiClient
})(window);
