import React, { useState, useRef, useEffect } from "react";
import styled from "styled-components";
import { Table, Button, notification, Spin, Menu, Dropdown } from "antd";
import Search from "../../../../components/search";
import XLSX from "xlsx";
import axios, { baseUrl } from "../../../../utils/axios";
// import axios from "axios";
import {
  PlusOutlined,
  ReloadOutlined,
  RightSquareOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import { useHistory } from "react-router-dom";
import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
// import { SEED_API } from "../../../GlobalVar";
// import ShowDevice from "../../seed/ShowSeedDevice";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../../components/input/main.styles";
import { StyledButton } from "../../../../components/button/main.styles";
import Modal from "./modal";
import Swal from "sweetalert2";
import { roles } from "../../../../utils/constants.js";

let columnFilters = {};
let excelData = [];

const Index = (props) => {
  const { height, width } = useWindowDimensions();
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  const [user, setUser] = useState();
  let [dataSource, setDataSource] = useState(excelData);
  let [showDev, setShowDev] = useState(false);
  let [deviceData, setDeviceData] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  let [editRecord, setEditRecord] = useState(null);
  let [searchSecValue, setSearchSecValue] = useState(null);
  let [searchNeValue, setSearchNeValue] = useState(null);
  let [inputNEValue, setInputNeValue] = useState("");
  let [inputSecValue, setInputSecValue] = useState("");
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const inputNe = useRef(null);
  const history = useHistory();
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const edit = (record) => {
    setEditRecord(record);
    showEditModal();
  };

  const showEditModal = () => {
    setIsModalVisible(true);
  };

  const opensweetalertdanger = (title) => {
    Swal.fire({
      title,
      type: "warning",
    });
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setUser(JSON.parse(localStorage.getItem("user")));
      setLoading(true);
      try {
        const res = await axios.get(baseUrl + "/iptAssignmentTracker");
        excelData = res.data;
        setDataSource(excelData);
        setRowCount(excelData.length);
        setLoading(false);
      } catch (err) {
        console.log(err.response);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter);
    setRowCount(extra.currentDataSource.length);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    setDataSource(excelData);
    setSortedInfo(null);
  };

  const handleNeInput = (e) => {
    let filteredSuggestions = excelData.filter(
      (d) =>
        JSON.stringify(d)
          .replace(" ", "")
          .toLowerCase()
          .indexOf(e.target.value.toLowerCase()) > -1
    );
    setRowCount(filteredSuggestions.length);
    setDataSource(filteredSuggestions);
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

  const openSweetAlert = (title, type) => {
    Swal.fire({
      title,
      type,
    });
  };

  const postNe = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/iptAssignmentTracker", seed)
      .then((response) => {
        console.log("rebd post response===>", response);
        if (response?.response?.status == 500) {
          openSweetAlert(response?.response?.data?.response, "error");
        } else {
          openSweetAlert("Items Added/Updated Successfully", "success");
        }
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/iptAssignmentTracker")
            .then((response) => {
              console.log("rebd response===>", response);
              excelData = response.data;
              setDataSource(excelData);
              setRowCount(excelData.length);
              setLoading(false);
            })
            .catch((error) => {
              console.log(error);
              setLoading(false);
            })
        );
        setLoading(false);
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setLoading(false);
      });
  };

  const importExcel = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    let data = null;
    reader.readAsBinaryString(file);
    reader.onload = (e) => {
      const bstr = e.target.result;
      const workbook = XLSX.read(bstr, { type: "binary" });
      const workSheetName = workbook.SheetNames[0];
      const workSheet = workbook.Sheets[workSheetName];
      const fileData = XLSX.utils.sheet_to_json(workSheet, { header: 1 });
      const headers = fileData[0];
      const heads = headers.map((head) => ({ title: head, field: head }));
      fileData.splice(0, 1);
      data = convertToJson(headers, fileData);
      postNe(data);
      console.log(data);
    };
  };

  useEffect(() => {
    inputNe.current.addEventListener("input", importExcel);
  }, []);

  sortedInfo = sortedInfo || {};

  const columns = [
    {
      title: "",
      key: "edit",
      width: "35px",

      render: (text, record) => (
        <a>
          <EditOutlined
            onClick={() => {
              edit(record);
            }}
          />
        </a>
      ),
    },
    {
      dataIndex: "employee_pf",
      key: "employee_pf",
      ...getColumnSearchProps(
        "employee_pf",
        "Employee PF",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      dataIndex: "full_name",
      key: "full_name",
      ...getColumnSearchProps(
        "full_name",
        "Full Name",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },

    {
      dataIndex: "organization",
      key: "organization",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "organization",
        "Organization",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_ip_address.localeCompare(b.switch_ip_address),
      // sortOrder:
      //   sortedInfo.columnKey === "switch_ip_address" && sortedInfo.order,
      ellipsis: true,
    },

    {
      dataIndex: "position",
      key: "position",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "position",
        "Position",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "grade",
      key: "grade",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "grade",
        "Grade",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "email",
      key: "email",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "email",
        "Email",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "mobile_number",
      key: "mobile_number",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "mobile_number",
        "Mobile Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "assigned_by",
      key: "assigned_by",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "assigned_by",
        "Assigned By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "ip_phone_model",
      key: "ip_phone_model",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "ip_phone_model",
        "IP Phone Model",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "serial_number",
      key: "serial_number",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "serial_number",
        "Serial Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "mac",
      key: "mac",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "mac",
        "MAC",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "date_of_device_assignment",
      key: "date_of_device_assignment",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "date_of_device_assignment",
        "Date Of Device Assignment",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "region",
      key: "region",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "region",
        "Region",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "registration_status",
      key: "registration_status",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "registration_status",
        "Registration Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.switch_name.localeCompare(b.switch_name),
      // sortOrder: sortedInfo.columnKey === "switch_name" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      // ...getColumnSearchProps("creation_date"),
      ...getColumnSearchProps(
        "creation_date",
        "Creation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.creation_date.length - b.creation_date.length,
      // sortOrder: sortedInfo.columnKey === "creation_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modification_date",
        "Modification Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "created_by",
      key: "created_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "created_by",
        "Created By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
    {
      dataIndex: "modified_by",
      key: "modified_by",
      // ...getColumnSearchProps("modification_date"),
      ...getColumnSearchProps(
        "modified_by",
        "Modified By",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.modification_date.length - b.modification_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "modification_date" && sortedInfo.order,
      ellipsis: true,
      hidden: user?.user_role !== roles.admin,
    },
  ].filter((item) => !item.hidden);

  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
  };

  const handleDelete = () => {
    if (selectedRowKeys.length > 0) {
      axios
        .delete(baseUrl + "/iptAssignmentTracker", {
          data: {
            ips: selectedRowKeys,
          },
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/iptAssignmentTracker")
              .then((response) => {
                console.log(response.data);
                setDataSource(response.data);
                excelData = response.data;
                setRowCount(excelData.length);
                setLoading(false);
              })
              .catch((error) => {
                console.log(error);
                setLoading(false);
              })
          );
          return Promise.all(promises);
        })
        .catch((err) => {
          console.log(err);
          setLoading(false);
        });
    } else {
      opensweetalertdanger("No item is selected to delete.");
    }
  };

  let seedTemp = [
    {
      employee_pf: "",
      full_name: "",
      organization: "",
      position: "",
      grade: "",
      email: "",
      ip_phone_model: "",
      serial_number: "",
      mac: "",
      date_of_device_assignment: "",
      region: "",
      registration_status: "",
    },
  ];

  const openNotification = () => {
    notification.open({
      message: "File Exported Successfully",
      onClick: () => {
        console.log("Notification Clicked!");
      },
    });
  };

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "iptassignmenttracker");
    XLSX.writeFile(wb, "iptassignmenttracker.xlsx");
    setExportLoading(false);
  };

  const exportTemplate = async () => {
    jsonToExcel(seedTemp);
    openNotification();
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
  };

  const exportFiltered = async () => {
    setExportLoading(true);
    jsonToExcel(dataSource);
    setExportLoading(false);
  };

  const menu = (
    <Menu style={{ marginTop: "-220px", height: "90px" }}>
      <Menu.Item
        key="0"
        style={{ backgroundColor: "transparent", padding: "0px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportSeed}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export All
        </StyledButton>
      </Menu.Item>
      <Menu.Item
        key="1"
        style={{ backgroundColor: "transparent", padding: "5px 10px" }}
      >
        <StyledButton
          color={"#3bbdc2"}
          onClick={exportFiltered}
          style={{ width: "100%" }}
        >
          <RightSquareOutlined /> Export Filtered
        </StyledButton>
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      <Spin tip="Loading..." spinning={loading}>
        {isModalVisible && (
          <Modal
            isModalVisible={isModalVisible}
            setIsModalVisible={setIsModalVisible}
            dataSource={dataSource}
            setDataSource={setDataSource}
            editRecord={editRecord}
            excelData={excelData}
          />
        )}

        <StyledHeading>
          IPT Assignment Tracker
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length - 1}
          </span>
        </StyledHeading>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <Search searchValue={searchNeValue} handleSeedInput={handleNeInput} />
          <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Add Item
          </StyledButton>
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 10px 0",
          }}
        >
          <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
            <RightSquareOutlined /> &nbsp; Delete
          </StyledButton>
          <div style={{ display: "flex" }}>
            <StyledButton color={"#3bbdc2"} onClick={exportTemplate}>
              <RightSquareOutlined /> &nbsp; Export Template
            </StyledButton>
            &nbsp;
            <Spin spinning={exportLoading}>
              <Dropdown overlay={menu} trigger={["click"]}>
                <StyledButton color={"#3bbdc2"}>
                  Export
                  <DownOutlined />
                </StyledButton>
              </Dropdown>
            </Spin>
            &nbsp;
            <StyledImportFileInput
              type="file"
              value={inputNEValue}
              onChange={() => importExcel}
              ref={inputNe}
            />
          </div>
        </div>
        <Table
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          size="small"
          scroll={{ x: 5000, y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="ip_assignment_tracker_id"
        />
      </Spin>
    </>
  );
};

export default Index;
