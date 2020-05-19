
export default {
  host: process.env.NODE_ENV === 'production'
      ? ''
      : 'http://localhost:8000/'
}
