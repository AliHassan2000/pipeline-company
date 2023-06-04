import React, { useState, useRef, useEffect, useContext } from "react";
import { Button, notification, Spin, Table, Menu, Dropdown } from "antd";
import Search from "../../../../components/search";
import { StyledTable } from "../../../../components/table/main.styles";
import { StyledButton } from "../../../../components/button/main.styles";
import { StyledHeading } from "../../../../components/paragraph/main.styles";
import { StyledImportFileInput } from "../../../../components/input/main.styles";
import Modal from "./modal";
import XLSX from "xlsx";
import Swal from "sweetalert2";

import { columnSearch } from "../../../../utils";
import useWindowDimensions from "../../../../hooks/useWindowDimensions";
import axios, { baseUrl } from "../../../../utils/axios";
import {
  RightSquareOutlined,
  ReloadOutlined,
  PlusOutlined,
  EditOutlined,
  DownOutlined,
} from "@ant-design/icons";
import { Context } from "../../../../context";
import { roles } from "../../../../utils/constants";

let columnFilters = {};
let excelData = [];
const Index = (props) => {
  const { height, width } = useWindowDimensions();
  // const { excelData, setExcelData, sntc, getSNTC } = useContext(Context);
  const [user, setUser] = useState();
  let [loading, setLoading] = useState(false);
  let [sortedInfo, setSortedInfo] = useState(null);
  let [filteredInfo, setFilteredInfo] = useState(null);
  let [exportLoading, setExportLoading] = useState(false);
  let [syncToLoading, setSyncToLoading] = useState(false);
  let [syncFromLoading, setSyncFromLoading] = useState(false);
  let [dataSource, setDataSource] = useState(excelData);
  let [searchValue, setSearchValue] = useState(null);
  let [inputValue, setInputValue] = useState("");
  let [editRecord, setEditRecord] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const inputRef = useRef(null);
  const searchRef = useRef(null);
  const [searchText, setSearchText] = useState(null);
  const [searchedColumn, setSearchedColumn] = useState(null);
  const [rowCount, setRowCount] = useState(0);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);

  let getColumnSearchProps = columnSearch(
    searchText,
    setSearchText,
    searchedColumn,
    setSearchedColumn
  );
  const opensweetalertdanger = (title) => {
    Swal.fire({
      title,
      type: "warning",
    });
  };

  useEffect(() => {
    const serviceCalls = async () => {
      setLoading(true);
      setUser(JSON.parse(localStorage.getItem("user")));
      try {
        // if (sntc.length === 0) {
        //   let data = await getSNTC();
        //   // console.log("papi chulo");
        //   console.log(data);
        //   setRowCount(data.length);
        //   setDataSource(data);
        // } else {
        //   setRowCount(excelData.length);
        //   setDataSource(excelData);
        // }

        await axios.get(baseUrl + "/getSNTC").then((response) => {
          console.log(response.data);
          setRowCount(response.data.length);
          setDataSource(response.data);
          excelData = response.data;
        });
        setLoading(false);
      } catch (err) {
        console.log(err);
        setLoading(false);
      }
    };
    serviceCalls();
  }, []);

  useEffect(() => {
    inputRef.current.addEventListener("input", importExcel);
  }, []);

  const openNotification = () => {
    notification.open({
      message: "File Exported Successfully",
      onClick: () => {
        console.log("Notification Clicked!");
      },
    });
  };

  const handleChange = (pagination, filters, sorter, extra) => {
    console.log("Various parameters", pagination, filters, sorter, extra);
    setRowCount(extra.currentDataSource.length);
    setFilteredInfo(filters);
    setSortedInfo(sorter);
  };

  const clearAll = () => {
    // console.log(searchRef.current.value);
    // searchRef.current.value = "";
    setSearchValue("");
    setDataSource(excelData);
    setRowCount(excelData.length);
    setSortedInfo(null);
  };

  const handleSeedInput = (e) => {
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

  const postSNTP = async (seed) => {
    setLoading(true);
    await axios
      .post(baseUrl + "/addSNTC", seed)
      .then((response) => {
        const promises = [];
        promises.push(
          axios.get(baseUrl + "/getSNTC").then((response) => {
            console.log(response.data);
            setRowCount(response.data.length);
            setDataSource(response.data);
            excelData = response.data;
            setLoading(false);
          })
        );
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setLoading(false);
      });

    // await getSNTC();
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
      let data = convertToJson(headers, fileData);
      excelData = data;
      // setExcelData(data);
      postSNTP(data);
      setRowCount(data.length);
      setDataSource(data);
    };
  };

  sortedInfo = sortedInfo || {};
  filteredInfo = filteredInfo || {};

  const showEditModal = () => {
    setIsModalVisible(true);
  };

  const edit = (record) => {
    setEditRecord(record);
    showEditModal();
  };

  const columns = [
    // {
    //   title: "Ip Address",
    //   dataIndex: "sntc_id",
    //   key: "sntc_id",
    //   ...getColumnSearchProps("sntc_id"),
    //   sorter: (a, b) => a.sntc_id - b.sntc_id,
    //   sortOrder: sortedInfo.columnKey === "sntc_id" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "",
      key: "edit",
      width: "2%",

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
      title: "Pn Code",
      dataIndex: "pn_code",
      key: "pn_code",
      // ...getColumnSearchProps("pn_code"),
      ...getColumnSearchProps(
        "pn_code",
        "Pn Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.pn_code.length - b.pn_code.length,
      // sortOrder: sortedInfo.columnKey === "pn_code" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_code",
      key: "item_code",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_code",
        "Item Code",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "item_desc",
      key: "item_desc",
      // ...getColumnSearchProps("authentication"),
      ...getColumnSearchProps(
        "item_desc",
        "Item Desc",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.authentication.length - b.authentication.length,
      // sortOrder: sortedInfo.columnKey === "authentication" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "VULN Fix Plan Status",
      dataIndex: "vuln_fix_plan_status",
      key: "vuln_fix_plan_status",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_fix_plan_status",
        "VULN Fix Plan Status",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      dataIndex: "vuln_ops_severity",
      key: "vuln_ops_severity",
      // ...getColumnSearchProps("source"),
      ...getColumnSearchProps(
        "vuln_ops_severity",
        "VULN OPS Severity",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.source.length - b.source.length,
      // sortOrder: sortedInfo.columnKey === "source" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "HW EOS Date",
      dataIndex: "hw_eos_date",
      key: "hw_eos_date",
      // ...getColumnSearchProps("hw_eos_date"),
      ...getColumnSearchProps(
        "hw_eos_date",
        "HW EOS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hw_eos_date.length - b.hw_eos_date.length,
      // sortOrder: sortedInfo.columnKey === "hw_eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "HW EOL Date",
      dataIndex: "hw_eol_date",
      key: "hw_eol_date",
      // ...getColumnSearchProps("hw_eol_date"),
      ...getColumnSearchProps(
        "hw_eol_date",
        "HW EOL Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.hw_eol_date.length - b.hw_eol_date.length,
      // sortOrder: sortedInfo.columnKey === "hw_eol_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "SW EOS Date",
      dataIndex: "sw_eos_date",
      key: "sw_eos_date",
      // ...getColumnSearchProps("sw_eos_date"),
      ...getColumnSearchProps(
        "sw_eos_date",
        "SW EOS Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sw_eos_date.length - b.sw_eos_date.length,
      // sortOrder: sortedInfo.columnKey === "sw_eos_date" && sortedInfo.order,
      ellipsis: true,
    },
    {
      title: "SW EOL Date",
      dataIndex: "sw_eol_date",
      key: "sw_eol_date",
      // ...getColumnSearchProps("sw_eol_date"),
      ...getColumnSearchProps(
        "sw_eol_date",
        "SW EOL Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.sw_eol_date.length - b.sw_eol_date.length,
      // sortOrder: sortedInfo.columnKey === "sw_eol_date" && sortedInfo.order,
      ellipsis: true,
    },
    // {
    //   title: "RFS Date",
    //   dataIndex: "rfs_date",
    //   key: "rfs_date",
    //   ...getColumnSearchProps("rfs_date"),
    //   sorter: (a, b) => a.rfs_date.length - b.rfs_date.length,
    //   sortOrder: sortedInfo.columnKey === "rfs_date" && sortedInfo.order,
    //   ellipsis: true,
    // },
    {
      title: "Manufacture Date",
      dataIndex: "manufactuer_date",
      key: "manufactuer_date",
      // ...getColumnSearchProps("manufactuer_date"),
      ...getColumnSearchProps(
        "manufactuer_date",
        "Manufacture Date",
        setRowCount,
        setDataSource,
        excelData,
        columnFilters
      ),
      // sorter: (a, b) => a.manufactuer_date.length - b.manufactuer_date.length,
      // sortOrder:
      //   sortedInfo.columnKey === "manufactuer_date" && sortedInfo.order,
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

  const jsonToExcel = (seedData) => {
    let wb = XLSX.utils.book_new();
    let binarySeedData = XLSX.utils.json_to_sheet(seedData);
    XLSX.utils.book_append_sheet(wb, binarySeedData, "seeds");
    XLSX.writeFile(wb, "sntc.xlsx");
  };

  let excelTemplate = [
    {
      sntc_id: "",
      pn_code: "",
      item_code: "",
      item_desc: "",
      vuln_fix_plan_status: "",
      vuln_ops_severity: "",
      hw_eos_date: "",
      hw_eol_date: "",
      sw_eos_date: "",
      sw_eol_date: "",
      rfs_date: "",
      manufactuer_date: "",
    },
  ];

  const exportTemplate = async () => {
    jsonToExcel(excelTemplate);
    openNotification();
  };

  const showModal = () => {
    setEditRecord(null);
    setIsModalVisible(true);
  };

  const exportSeed = async () => {
    setExportLoading(true);
    jsonToExcel(excelData);
    setExportLoading(false);
  };

  const syncTo = async () => {
    setSyncToLoading(true);
    await axios
      .get(baseUrl + "/syncToInventory")
      .then((response) => {
        setSyncToLoading(false);
      })
      .catch((err) => {
        console.log(err);
        setSyncToLoading(false);
      });
  };
  const handleDelete = () => {
    if (selectedRowKeys.length > 0) {
      axios
        .post(baseUrl + "/deletePnCode", {
          user_ids: selectedRowKeys,
        })

        .then(() => {
          const promises = [];
          promises.push(
            axios
              .get(baseUrl + "/getSNTC")
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
      opensweetalertdanger("No PN Code is selected to delete.");
    }
  };
  const syncFrom = async () => {
    setSyncFromLoading(true);
    await axios
      .get(baseUrl + "/syncFromInventory")
      .then((response) => {
        const promises = [];
        promises.push(
          axios.get(baseUrl + "/getSNTC").then((response) => {
            console.log(response.data);
            setRowCount(response.data.length);
            setDataSource(response.data);
            excelData = response.data;
            setSyncFromLoading(false);
          })
        );
        return Promise.all(promises);
      })
      .catch((err) => {
        console.log(err);
        setSyncFromLoading(false);
      });

    // await getSNTC();
  };
  const onSelectChange = (selectedRowKeys) => {
    console.log("selectedRowKeys changed: ", selectedRowKeys);
    setSelectedRowKeys(selectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
    selection: Table.SELECTION_ALL,
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
            excelData={excelData}
            editRecord={editRecord}
          />
        )}

        <StyledHeading>
          SNTC List
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
          <Search
            searchValue={searchValue}
            handleSeedInput={handleSeedInput}
            // ref={searchRef}
          />
          {/* <StyledButton onClick={showModal} color={"#009BDB"}>
            <PlusOutlined /> &nbsp; Add SNTC
          </StyledButton>  */}
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            padding: "0 0 2px 0",
          }}
        >
          <div style={{ display: "flex" }}>
            <StyledButton onClick={handleDelete} color={"#bb0a1e"}>
              <RightSquareOutlined /> &nbsp; Delete
            </StyledButton>
            &nbsp;
            <Spin spinning={syncToLoading}>
              <StyledButton color={"#3bbdc2"} onClick={syncTo}>
                <RightSquareOutlined /> &nbsp; Sync To Inventory
              </StyledButton>
            </Spin>
            &nbsp;
            <Spin spinning={syncFromLoading}>
              <StyledButton color={"#3bbdc2"} onClick={syncFrom}>
                <RightSquareOutlined /> &nbsp; Sync From Inventory
              </StyledButton>
            </Spin>
            {/* <div>
              <Button
                style={{
                  border: "none",
                  backgroundColor: "transparent",
                  marginTop: "-4px",
                }}
                onClick={clearAll}
              >
                <ReloadOutlined
                  style={{
                    color: "#009BDB",
                    fontSize: "20px",
                    padding: "0px",
                    margin: "0px",
                  }}
                />
              </Button>
            </div> */}
          </div>
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
            <div>
              <StyledImportFileInput
                type="file"
                value={inputValue}
                onChange={() => importExcel}
                ref={inputRef}
              />
            </div>
          </div>
        </div>
        <StyledTable
          rowSelection={rowSelection}
          pagination={{
            defaultPageSize: 50,
            pageSizeOptions: [50, 100, 500, 1000],
          }}
          scroll={{ x: 2500, y: height - 350 }}
          onChange={handleChange}
          columns={columns}
          dataSource={dataSource}
          rowKey="pn_code"
        />
      </Spin>
    </>
  );
};

export default Index;
