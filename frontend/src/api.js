import { auth } from './firebase'

export async function authenticatedFetch(url, options = {}) {
  const user = auth.currentUser
  if (!user) {
    throw new Error('No authenticated user')
  }

  const token = await user.getIdToken()
  const isFormData =
    typeof FormData !== 'undefined' && options.body instanceof FormData

  const headers = {
    ...options.headers,
    Authorization: `Bearer ${token}`,
  }

  if (!isFormData && !headers['Content-Type'] && !headers['content-type']) {
    headers['Content-Type'] = 'application/json'
  }

  return fetch(url, {
    ...options,
    headers,
  })
}
