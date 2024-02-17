import React from 'react'

const TextBox = ({label, placeholder, id, onChange}) => {
  return (
    <div className='grid gap-5 grid-cols-2 mt-2' id={id}>
        <label>{label}</label>
        <input type='text' placeholder={placeholder} onChange={onChange}/>
    </div>
  )
}

export default TextBox