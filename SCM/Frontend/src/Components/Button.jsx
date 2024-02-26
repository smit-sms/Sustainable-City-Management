import React from 'react'

const Button = ({on_click, children}) => {
  return (
    <button onClick={on_click} className='bg-slate-300 border-2 py-2 px-3 font-bold text-center rounded-lg hover:bg-slate-400'>
        {children}
    </button>
  )
}

export default Button;