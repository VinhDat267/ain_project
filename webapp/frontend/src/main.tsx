import '@fontsource/funnel-display/400.css'
import '@fontsource/funnel-display/500.css'
import '@fontsource/funnel-sans/400.css'
import '@fontsource/funnel-sans/500.css'
import '@fontsource/funnel-sans/600.css'
import '@fontsource/dm-mono/400.css'
import '@fontsource/dm-mono/500.css'

import './styles/tokens.css'
import './styles/app.css'

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
