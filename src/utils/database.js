const DB_NAME = 'LeafSortDB'
const DB_VERSION = 1

const STORES = {
  photos: 'photos',
  people: 'people',
  places: 'places',
  events: 'events',
  albums: 'albums',
  tags: 'tags'
}

class IndexedDBHelper {
  constructor() {
    this.db = null
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => reject(request.error)

      request.onsuccess = () => {
        this.db = request.result
        resolve(this.db)
      }

      request.onupgradeneeded = (event) => {
        const db = event.target.result

        if (!db.objectStoreNames.contains(STORES.photos)) {
          const photoStore = db.createObjectStore(STORES.photos, { keyPath: 'id' })
          photoStore.createIndex('date', 'date', { unique: false })
          photoStore.createIndex('people', 'people', { unique: false, multiEntry: true })
          photoStore.createIndex('places', 'places', { unique: false, multiEntry: true })
          photoStore.createIndex('events', 'events', { unique: false, multiEntry: true })
          photoStore.createIndex('tags', 'tags', { unique: false, multiEntry: true })
        }

        if (!db.objectStoreNames.contains(STORES.people)) {
          const peopleStore = db.createObjectStore(STORES.people, { keyPath: 'id' })
          peopleStore.createIndex('name', 'name', { unique: false })
        }

        if (!db.objectStoreNames.contains(STORES.places)) {
          const placesStore = db.createObjectStore(STORES.places, { keyPath: 'id' })
          placesStore.createIndex('name', 'name', { unique: false })
        }

        if (!db.objectStoreNames.contains(STORES.events)) {
          const eventsStore = db.createObjectStore(STORES.events, { keyPath: 'id' })
          eventsStore.createIndex('date', 'date', { unique: false })
        }

        if (!db.objectStoreNames.contains(STORES.albums)) {
          const albumsStore = db.createObjectStore(STORES.albums, { keyPath: 'id' })
          albumsStore.createIndex('name', 'name', { unique: false })
        }

        if (!db.objectStoreNames.contains(STORES.tags)) {
          const tagsStore = db.createObjectStore(STORES.tags, { keyPath: 'name' })
          tagsStore.createIndex('count', 'count', { unique: false })
        }
      }
    })
  }

  async add(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.add(data)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async put(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.put(data)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async get(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.get(key)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async getAll(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.getAll()

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async getByIndex(storeName, indexName, value) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const index = store.index(indexName)
      const request = index.getAll(value)

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async delete(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.delete(key)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  async clear(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.clear()

      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  async count(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly')
      const store = transaction.objectStore(storeName)
      const request = store.count()

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }
}

const dbHelper = new IndexedDBHelper()

export { dbHelper, STORES }
