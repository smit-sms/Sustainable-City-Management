import React from 'react'

const RadioButton = ({label, name, id, value, selected, uponClick}) => {
  return (
    <div id={id} className='radio-button'>
        {
            selected ? 
            <input className='mr-2' type="radio" name={name} value={value} defaultChecked onClick={uponClick} /> :
            <input className='mr-2' type="radio" name={name} value={value} onClick={uponClick} />
        }
        <label>{label}</label>
    </div>
  )
}

export default RadioButton