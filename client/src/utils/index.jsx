import React, { useState } from "react";
import { Button, Space, Input } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import Highlighter from "react-highlight-words";
// import { debounce } from "throttle-debounce";

const ColumnHeader = ({
  dataIndex,
  title,
  setRowCount,
  setDataSource,
  excelData,
  columnFilters,
}) => {
  const [searchText, setSearchText] = useState(null);

  const handleColumnInput = (e) => {
    // setSearchText(e.target.value);
    console.log("hello");
    if (dataIndex in columnFilters) {
      if (e.target.value.length > 0) columnFilters[dataIndex] = e.target.value;
      else delete columnFilters[dataIndex];
    } else {
      columnFilters[dataIndex] = e.target.value;
    }
    let filteredSuggestions = excelData;
    console.log(e.target.value);
    console.log(dataIndex);
    console.log(columnFilters);

    for (const [key, value] of Object.entries(columnFilters)) {
      filteredSuggestions = filteredSuggestions.filter(
        (d) =>
          JSON.stringify(d[key])
            ?.replace(" ", "")
            .toLowerCase()
            .indexOf(value.replace(" ", "").toLowerCase()) > -1
      );
    }

    setRowCount(filteredSuggestions.length);
    setDataSource(filteredSuggestions);
  };

  return (
    <div style={{ textAlign: "center" }}>
      <div>{title}</div>
      <Input
        style={{ height: "25px", borderRadius: "5px", marginTop: "5px" }}
        // value={searchText}
        // onKeyUp={debounce(handleColumnInput, 750)}
        // onChange={debounce(750, handleColumnInput)}
        onChange={handleColumnInput}
      />
    </div>
  );
};

export const columnSearch = (
  searchText,
  setSearchText,
  searchedColumn,
  setSearchedColumn
) => {
  //-------------------------------------------------------------------------------------------
  let searchInput = null;
  const getColumnSearchProps = (
    dataIndex,
    title,
    setRowCount,
    setDataSource,
    excelData,
    columnFilters
  ) => ({
    title: (
      <ColumnHeader
        dataIndex={dataIndex}
        title={title}
        setRowCount={setRowCount}
        setDataSource={setDataSource}
        excelData={excelData}
        columnFilters={columnFilters}
      />
    ),
    // filterDropdown: ({
    //   setSelectedKeys,
    //   selectedKeys,
    //   confirm,
    //   clearFilters,
    // }) => (
    //   <div style={{ padding: 8, marginTop: "-225px" }}>
    //     <Input
    //       ref={(node) => {
    //         searchInput = node;
    //       }}
    //       placeholder={`Search ${dataIndex}`}
    //       value={selectedKeys[0]}
    //       onChange={(e) =>
    //         setSelectedKeys(e.target.value ? [e.target.value] : [])
    //       }
    //       onPressEnter={() => handleSearch(selectedKeys, confirm, dataIndex)}
    //       style={{ marginBottom: 8, display: "block" }}
    //     />
    //     <Space>
    //       <Button
    //         type="primary"
    //         onClick={() => handleSearch(selectedKeys, confirm, dataIndex)}
    //         icon={<SearchOutlined />}
    //         size="small"
    //         style={{ width: 90 }}
    //       >
    //         Search
    //       </Button>
    //       <Button
    //         onClick={() => handleReset(clearFilters)}
    //         size="small"
    //         style={{ width: 90 }}
    //       >
    //         Reset
    //       </Button>
    //       <Button
    //         type="link"
    //         size="small"
    //         onClick={() => {
    //           confirm({ closeDropdown: false });
    //           setSearchText(selectedKeys[0]);
    //           setSearchedColumn(dataIndex);
    //         }}
    //       >
    //         Filter
    //       </Button>
    //     </Space>
    //   </div>
    // ),

    // filterIcon: (filtered) => (
    //   <SearchOutlined style={{ color: filtered ? "#1890ff" : undefined }} />
    // ),

    // onFilter: (value, record) =>
    //   record[dataIndex]
    //     ? record[dataIndex]
    //         .toString()
    //         .toLowerCase()
    //         .includes(value.toLowerCase())
    //     : "",

    // onFilterDropdownVisibleChange: (visible) => {
    //   if (visible) {
    //     setTimeout(() => searchInput.select(), 100);
    //   }
    // },

    // render: (text) =>
    //   searchedColumn === dataIndex ? (
    //     <Highlighter
    //       highlightStyle={{ backgroundColor: "#ffc069", padding: 0 }}
    //       searchWords={[searchText]}
    //       autoEscape
    //       textToHighlight={text ? text.toString() : ""}
    //     />
    //   ) : (
    //     text
    //   ),
  });

  const handleSearch = (selectedKeys, confirm, dataIndex) => {
    confirm();
    setSearchText(selectedKeys[0]);
    setSearchedColumn(dataIndex);
  };

  const handleReset = (clearFilters) => {
    clearFilters();
    setSearchText("");
  };

  return getColumnSearchProps;
  //-------------------------------------------------------------------------------------------
};
