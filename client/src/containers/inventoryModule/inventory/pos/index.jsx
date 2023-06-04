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
import { roles } from "../../../../utils/constants";

let columnFilters = {};
let excelData = [];

const Index = (props) => {
  const { height, width } = useWindowDimensions();
  const [user, setUser] = useState();
  let [loading, setLoading] = useState(false);
  let [exportLoading, setExportLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
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

  const opensweetalertdanger = () => {
    Swal.fire({
      title: "NO Device Data Found!",
      // text: "OOPS",
      type: "warning",
    });
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      try {
        const res = await axios.get(baseUrl + "/getAllPoss");
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

  const showDeviceData = async (device_ip, device_type) => {
    await axios
      .post(baseUrl + "/showEDNInventoryData", {
        ip: device_ip,
        type: device_type,
      })
      .then((res) => {
        if ("msg" in res.data) {
          opensweetalertdanger();
          // alert("NO Device Data Found");
        } else {
          setDeviceData(res.data);
          setShowDev(true);
          console.log("device data===>", res.data);
        }
      })
      .catch((er) => {
        console.log("error", er);
      });
  };

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

  const postNe = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addPoss", seed)
      .then((response) => {
        console.log("cdn post response===>", response);
        const promises = [];
        promises.push(
          axios
            .get(baseUrl + "/getAllPoss")
            .then((response) => {
              console.log("cdn response===>", response);
              excelData = response.data;
              setDataSource(excelData);
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
      title: "NE IP Address",
      dataIndex: "ne_ip_address",
      key: "ne_ip_address",
      ...getColumnSearchProps(
        "ne_ip_address",
        "NE IP Address",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Device ID",
      dataIndex: "device_id",
      key: "device_id",
      ...getColumnSearchProps(
        "device_id",
        "Device ID",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },

    {
      dataIndex: "site_id",
      key: "site_id",
      // ...getColumnSearchProps("switch_ip_address"),
      ...getColumnSearchProps(
        "site_id",
        "Site ID",
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
      dataIndex: "rack_id",
      key: "rack_id",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "rack_id",
        "Rack Id",
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
      dataIndex: "longitude",
      key: "longitude",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "longitude",
        "Longitude",
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
      dataIndex: "latitude",
      key: "latitude",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "latitude",
        "Latitude",
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
      dataIndex: "city",
      key: "city",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "city",
        "City",
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
      dataIndex: "floor",
      key: "floor",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "floor",
        "Floor",
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
      dataIndex: "pn_code",
      key: "pn_code",
      // ...getColumnSearchProps("switch_name"),
      ...getColumnSearchProps(
        "pn_code",
        "PN Code",
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
      title: "Tag ID",
      dataIndex: "tag_id",
      key: "tag_id",
      ...getColumnSearchProps(
        "tag_id",
        "Tag ID",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "RFS Date",
      dataIndex: "rfs_date",
      key: "rfs_date",
      ...getColumnSearchProps(
        "rfs_date",
        "RFS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },

    {
      title: "Device RU",
      dataIndex: "device_ru",
      key: "device_ru",
      ...getColumnSearchProps(
        "device_ru",
        "Device RU",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Department",
      dataIndex: "department",
      key: "department",
      ...getColumnSearchProps(
        "department",
        "Department",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Section",
      dataIndex: "section",
      key: "section",
      ...getColumnSearchProps(
        "section",
        "Section",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Criticality",
      dataIndex: "criticality",
      key: "criticality",
      ...getColumnSearchProps(
        "criticality",
        "Criticality",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Function",
      dataIndex: "function",
      key: "function",
      ...getColumnSearchProps(
        "function",
        "Function",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Domain",
      dataIndex: "domain",
      key: "domain",
      ...getColumnSearchProps(
        "domain",
        "Domain",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Virtual",
      dataIndex: "virtual",
      key: "virtual",
      ...getColumnSearchProps(
        "virtual",
        "Virtual",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Authentication",
      dataIndex: "authentication",
      key: "authentication",
      ...getColumnSearchProps(
        "authentication",
        "Authentication",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Hostname",
      dataIndex: "hostname",
      key: "hostname",
      ...getColumnSearchProps(
        "hostname",
        "Hostname",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "SW Type",
      dataIndex: "sw_type",
      key: "sw_type",
      ...getColumnSearchProps(
        "sw_type",
        "SW Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Vendor",
      dataIndex: "vendor",
      key: "vendor",
      ...getColumnSearchProps(
        "vendor",
        "Vendor",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Operation Status",
      dataIndex: "operation_status",
      key: "operation_status",
      ...getColumnSearchProps(
        "operation_status",
        "Operation Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Site Type",
      dataIndex: "site_type",
      key: "site_type",
      ...getColumnSearchProps(
        "site_type",
        "Site Type",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Contract Expiry",
      dataIndex: "contract_expiry",
      key: "contract_expiry",
      ...getColumnSearchProps(
        "contract_expiry",
        "Contract Expiry",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Contract Number",
      dataIndex: "contract_number",
      key: "contract_number",
      ...getColumnSearchProps(
        "contract_number",
        "Contract Number",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Stack",
      dataIndex: "stack",
      key: "stack",
      ...getColumnSearchProps(
        "stack",
        "Stack",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Creation Date",
      dataIndex: "creation_date",
      key: "creation_date",
      ...getColumnSearchProps(
        "creation_date",
        "Creation Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    {
      title: "Modification Date",
      dataIndex: "modification_date",
      key: "modification_date",
      ...getColumnSearchProps(
        "modification_date",
        "Modification Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      ellipsis: true,
    },
    // {
    //   title: "Subrack Id Number",
    //   dataIndex: "subrack_id_number",
    //   key: "subrack_id_number",
    //   ...getColumnSearchProps(
    //     "subrack_id_number",
    //     "Subrack Id Number",
    //     setRowCount,
    //     setDataSource,
    //     excelData,
    //     columnFilters
    //   ),
    //   ellipsis: true,
    // },
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
        .post(baseUrl + "/deletePos", {
          ne_ip_address: selectedRowKeys,
        })
        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getAllPoss")
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
      opensweetalertdanger("No device is selected to delete.");
    }
  };

  let seedTemp = [
    {
      site_id: "",
      rack_id: "",
      latitude: "",
      longitude: "",
      region: "",
      city: "",
      floor: "",
      serial_number: "",
      pn_code: "",
      tag_id: "",
      rfs_date: "",
      device_id: "",
      ne_ip_address: "",
      device_ru: "",
      department: "",
      section: "",
      criticality: "",
      function: "",
      domain: "",
      virtual: "",
      authentication: "",
      hostname: "",
      sw_type: "",
      vendor: "",
      operation_status: "",
      site_type: "",
      contract_expiry: "",
      contract_number: "",
      stack: "",
      // asset_type: "",
      // subrack_id_number: "",
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
    XLSX.utils.book_append_sheet(wb, binarySeedData, "pos");
    XLSX.writeFile(wb, "pos.xlsx");
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
    jsonToExcel(dataSource, "filteredednmaclegacy.xlsx");
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
          />
        )}

        <StyledHeading>
          POS
          <span
            style={{
              float: "right",
              fontSize: "14px",
              fontWeight: "bold",
              color: "grey",
              paddingTop: "10px",
            }}
          >
            Rows: {rowCount} &nbsp;&nbsp;&nbsp; Columns: {columns.length}
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
            <PlusOutlined /> &nbsp; ADD DEVICE
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
          scroll={{ x: 8000, y: height - 350 }}
          onChange={handleChange}
          rowSelection={rowSelection}
          columns={columns}
          dataSource={dataSource}
          rowKey="ne_ip_address"
        />
      </Spin>
    </>
  );
};

export default Index;
