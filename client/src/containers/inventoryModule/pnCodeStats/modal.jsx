import React, { useEffect, useState, useRef } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import Swal from "sweetalert2";
import { DatePicker } from "antd";
import XLSX from "xlsx";

const AddDeviceModal = (props) => {
  let [date, setDate] = useState(null);
  let [data, setData] = useState(null);
  let [inputValue, setInputValue] = useState("");
  const inputRef = useRef(null);

  //   useEffect(() => {
  //     inputRef.current.addEventListener("input", importExcel);
  //   }, []);

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const handleSubmit = async () => {
    if (date == null) {
      alert("kindly select a date");
    } else if (data == null) {
      alert("kindly import an excel file");
    } else {
      //   console.log(date);
      //   console.log(data);

      props.setLoading(true);
      await axios
        .post(baseUrl + "/addPnCodeSnap", { date, data })
        .then((response) => {
          if (response?.response?.status == 500) {
            openSweetAlert(response?.response?.data?.response, "error");
          } else {
            openSweetAlert(`All PN-Code Stats Added Successfully`, "success");
          }
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getPNCodeStatsPerCiscoDomain")
              .then((response) => {
                console.log("response===>", response);
                props.excelData = response.data;
                props.setDataSource(props.excelData);
                props.setRowCount(props.excelData.length);
                props.setLoading(false);
                props.setIsModalVisible(false);
              })
              .catch((error) => {
                console.log(error);
                props.setLoading(false);
                props.setIsModalVisible(false);
              })
          );
          props.setLoading(false);
          props.setIsModalVisible(false);
          return Promise.all(promises);
        })
        .catch((err) => {
          console.log(err);
          props.setIsModalVisible(false);
          props.setLoading(false);
        });
      props.setIsModalVisible(false);
    }
  };

  const handleCancel = () => {
    props.setIsModalVisible(false);
  };

  const convertToJson = (headers, fileData) => {
    let rows = [];
    fileData.forEach((row) => {
      const rowData = {};
      row.forEach((element, index) => {
        rowData[headers[index]] = element;
      });
      rows.push(rowData);
    });
    rows = rows.filter((value) => JSON.stringify(value) !== "{}");
    return rows;
  };

  const importExcel = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.readAsBinaryString(file);
    reader.onload = (e) => {
      const bstr = e.target.result;
      const workbook = XLSX.read(bstr, { type: "binary" });
      const workSheetName = workbook.SheetNames[0];
      const workSheet = workbook.Sheets[workSheetName];
      const fileData = XLSX.utils.sheet_to_json(workSheet, {
        header: 1,
        raw: false,
      });
      const headers = fileData[0];
      fileData.splice(0, 1);
      let jsonData = convertToJson(headers, fileData);
      setData(jsonData);
    };
    // e.target.value = null;
  };

  function onChange(date, dateString) {
    console.log(date, dateString);
    setDate(dateString);
  }

  return (
    <Modal
      style={{ marginTop: "40px", zIndex: "99999" }}
      //   width="60%"
      title=""
      closable={false}
      visible={props.isModalVisible}
      footer=""
    >
      <Row>
        <Col span={24} style={{ textAlign: "center" }}>
          <DatePicker onChange={onChange} />
          {/* <br />
          <br /> */}
          &nbsp;&nbsp;&nbsp;
          <input
            type="file"
            // value={inputValue}
            onChange={importExcel}
            // ref={inputRef}
          />
          <br />
          <br />
        </Col>
        <Col span={24} style={{ textAlign: "center" }}>
          <StyledButton color={"red"} onClick={handleCancel}>
            Cancel
          </StyledButton>
          &nbsp; &nbsp;
          <StyledButton color={"green"} onClick={handleSubmit}>
            Import
          </StyledButton>
        </Col>
      </Row>
    </Modal>
  );
};

const StyledInput = styled(Input)`
  height: 1.6rem;
`;

const InputWrapper = styled.div`
  font-size: 12px;
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  padding-bottom: 10px;
`;

const StyledSubmitButton = styled(Input)`
  font-size: 11px;
  font-weight: bolder;
  width: 30%;
  font-family: Montserrat-Regular;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;

const StyledButton = styled(Button)`
  height: 27px;
  font-size: 11px;
  font-weight: bolder;
  width: 30%;
  font-family: Montserrat-Regular;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  background-color: ${(props) => props.color};
  border-color: ${(props) => props.color};
  color: white;
  border-radius: 5px;
  &:focus,
  &:hover {
    background-color: ${(props) => props.color};
    border-color: ${(props) => props.color};
    color: white;
    opacity: 0.8;
  }
`;

export default AddDeviceModal;
