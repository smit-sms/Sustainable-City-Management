import React from 'react'

const TextBox = ({label, placeholder, id, onChange, isEditable}) => {
  return (
    <div className='grid gap-5 grid-cols-2 mt-2' id={id}>
        <label>{label}</label>
        {
            isEditable ? 
            <input className='rounded-sm hover:outline hover:outline-slate-200 outline-rounded-lg' type='text' placeholder={placeholder} onChange={onChange}/> :
            <input type='text' placeholder={placeholder} onChange={onChange} disabled/>
        }
        
    </div>
  )
}

export default TextBox