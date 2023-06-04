import React, { useState, useEffect, useRef } from "react";
import styled from "styled-components";
import { Row, Col, Modal, Input, Button, Select, Spin } from "antd";
import axios, { baseUrl } from "../../../utils/axios";
import { getConfig } from "@testing-library/react";
import Swal from "sweetalert2";
import MultiSelect from "react-select";
import XLSX from "xlsx";
import {
  RightSquareOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";

const Index = (props) => {
  const [devicesColumns, setDevicesColumns] = useState([]);
  const [data, setData] = useState([]);
  const [options, setOptions] = useState([]);
  const [inputValue, setInputValue] = useState("");
  let [exportLoading, setExportLoading] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    const apiCalls = async () => {
      try {
        await axios
          .get(baseUrl + "/getAllDeviceStaticColumns")
          .then((res) => {
            setOptions(res.data);
          })
          .catch((err) => {
            console.log(err);
          });
      } catch (e) {
        console.log(e);
      }
    };
    apiCalls();
  }, []);

  // useEffect(() => {
  //   inputRef.current.addEventListener("input", importExcel);
  // }, []);

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
    console.log(file);
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
      let excelData = convertToJson(headers, fileData);
      setData(excelData);
    };
  };

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postDevice = async (columns) => {
    try {
      await axios
        .post(baseUrl + "/bulkUpdateDeviceExcel", { columns, data })
        .then((res) => {
          console.log(res.data);
          if (res.data?.code === "200") {
            openSweetAlert(res.data.response, "success");
          } else {
            openSweetAlert(res.data.response, "danger");
          }
        })
        .catch((err) => {
          console.log(err);
        });
    } catch (err) {
      console.log(err);
    }
  };

  const handleSubmitDevices = (e) => {
    e.preventDefault();
    let columns = devicesColumns.map((item) => item.value);
    console.log(columns);
    postDevice(columns);
  };

  const handleCancelDevices = () => {
    setDevicesColumns([]);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      background: "#fff",
      borderColor: "#9e9e9e",
      minHeight: "30px",
      // height: "30px",
      boxShadow: state.isFocused ? null : null,
    }),

    valueContainer: (provided, state) => ({
      ...provided,
      // height: "30px",
      // padding: "0 6px",
    }),

    input: (provided, state) => ({
      ...provided,
      margin: "0px",
    }),
    indicatorSeparator: (state) => ({
      display: "none",
    }),
    indicatorsContainer: (provided, state) => ({
      ...provided,
      height: "30px",
    }),
  };

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "devices");
    XLSX.writeFile(wb, "devices.xlsx");
    setExportLoading(false);
  };

  const exportAllDevices = async () => {
    setExportLoading(true);
    // jsonToExcel(excelData);
    // setExportLoading(false);
    await axios
      .get(baseUrl + "/getAllDevices")
      .then((response) => {
        jsonToExcel(response.data);
        console.log(response);
      })
      .catch((error) => {
        setExportLoading(false);
        console.log(error);
      });
  };

  return (
    <div style={{ border: "0px solid green", position: "fixed", width: "79%" }}>
      <form onSubmit={handleSubmitDevices} style={{ border: "0px solid blue" }}>
        <StyledCard style={{ border: "0px solid red" }}>
          <Row gutter={30}>
            <Col span={4}></Col>
            <Col span={16} style={{ textAlign: "center" }}>
              <p style={{ fontSize: "22px" }}>Update Devices by Excel</p>
            </Col>
            <Col span={4}>
              <Spin spinning={exportLoading}>
                <StyledButton
                  color={"#3bbdc2"}
                  onClick={exportAllDevices}
                  style={{ width: "100%" }}
                >
                  <RightSquareOutlined /> Export All Devices
                </StyledButton>
              </Spin>
            </Col>
            <Col span={24}>
              <InputWrapper>
                Device Columns To Update: &nbsp;
                <span style={{ color: "red" }}>*</span>
                &nbsp;&nbsp;
                <div style={{ width: "100%" }}>
                  <MultiSelect
                    isMulti
                    styles={customStyles}
                    value={devicesColumns}
                    onChange={(e) => setDevicesColumns(e)}
                    options={options}
                  />
                </div>
              </InputWrapper>
              <InputWrapper>
                <div style={{ display: "flex" }}>
                  Select Excel File With Updated Data: &nbsp;
                  <span style={{ color: "red" }}>*</span>
                  &nbsp;&nbsp;
                  <div>
                    <input
                      type="file"
                      // value={inputValue}
                      onChange={() => importExcel}
                      ref={inputRef}
                    />
                  </div>
                </div>
              </InputWrapper>
            </Col>
            <Col span={24} style={{ textAlign: "center" }}>
              <StyledButton color={"red"} onClick={handleCancelDevices}>
                Cancel
              </StyledButton>
              &nbsp; &nbsp;{" "}
              <StyledSubmitButton
                color={"green"}
                type="submit"
                value="Update"
              />
            </Col>
          </Row>
        </StyledCard>
      </form>
    </div>
  );
};

const StyledCard = styled.div`
  /* margin-top: -10px; */
  margin-bottom: 20px;
  /* height: 100%; */
  /* text-align: center; */
  background-color: white;
  border-radius: 10px;
  padding: 10px 20px 20px 20px;
  box-shadow: rgba(99, 99, 99, 0.2) 0px 2px 8px 0px;
`;

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
  width: 15%;
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
  width: 15%;
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

export default Index;
