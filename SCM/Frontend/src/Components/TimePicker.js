import React, { useState, useEffect } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import BikeMap from "./BikeMap";
// import addHours from "date-fns/addHours";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const BikeAvailabilityPicker = () => {
	const [startDate, setStartDate] = useState(new Date());
	const [today, setToday] = useState(new Date());
	const tomorrow = new Date();
	// let tomorrow = new Date();
	tomorrow.setDate(tomorrow.getDate() + 1);
	const [minTime, setMinTime] = useState(new Date());
	const [maxTime, setMaxTime] = useState(new Date());

	useEffect(() => {
		setMaxTime(
			new Date(
				tomorrow.getFullYear(),
				tomorrow.getMonth(),
				tomorrow.getDate(),
				23,
				59
			)
		);
	}, []);

	// console.log(tomorrow);
	// console.log(maxTime);

	useEffect(() => {
		if (
			startDate.getDate() === today.getDate() &&
			startDate.getMonth() === today.getMonth() &&
			startDate.getFullYear() === today.getFullYear()
		) {
			setMinTime(new Date());
			setMaxTime(
				new Date(
					tomorrow.getFullYear(),
					tomorrow.getMonth(),
					tomorrow.getDate(),
					23,
					59
				)
			);
		} else {
			setMinTime(
				new Date(
					tomorrow.getFullYear(),
					tomorrow.getMonth(),
					tomorrow.getDate(),
					0,
					0
				)
			);
			setMaxTime(
				new Date(
					tomorrow.getFullYear(),
					tomorrow.getMonth(),
					tomorrow.getDate(),
					today.getHours(),
					59
				)
			);
			// console.log(maxTime);
		}
	}, [startDate]);

	return (
		<div>
			<div className="date-picker-container relative z-20">
				<DatePicker
					selected={startDate}
					onChange={(date) => {
						setStartDate(date);
						// onTimeChange(date); // Call the passed callback function
					}}
					showTimeSelect
					dateFormat="MMMM d, yyyy h:mm aa"
					// minDate={new Date()}
					// maxDate={addHours(new Date(), 24)} // 1 year from now
					timeIntervals={60}
					minDate={today}
					maxDate={tomorrow}
					minTime={minTime}
					maxTime={maxTime}
					// dateFormat="MMMM d, yyyy h:mm aa"
				/>
			</div>
			<ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} theme="colored" pauseOnFocusLoss draggable pauseOnHover />
			<div className="relative z-10">
				<BikeMap currSetTime={startDate.getTime()} toast={toast} className="h-full z-10" />
			</div>
		</div>
	);
};

export default BikeAvailabilityPicker;
