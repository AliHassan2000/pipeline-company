import React, { useEffect, useState, useRef } from "react";
import { Route } from "react-router-dom";
import { WalletOutlined } from "@ant-design/icons";
import { StyledMenuItem, StyledMenu } from "../landing/styles/main.styles";
import AccessPoints from "../accessPointsModule/accessPoints";

export const AccessPointsMenu = ({ user, roles, history, location }) => {
  return (
    <>
      <StyledMenu
        user={user?.user_role}
        defaultSelectedKeys={["/"]}
        selectedKeys={[`/${location.pathname.split("/")[1]}`]}
        mode="inline"
        inlineCollapsed={false}
      >
        <>
          <StyledMenuItem
            key="/accesspoints"
            icon={<WalletOutlined />}
            onClick={() => history.push("/accesspoints")}
          >
            Access Points
          </StyledMenuItem>
        </>
      </StyledMenu>
    </>
  );
};

export const AccessPointsRoutes = ({ user, roles }) => {
  return (
    <>
      {user?.user_role !== roles.ednSM ? (
        <>
          {user?.user_role !== roles.executive ? (
            <Route exact path="/accesspoints" component={AccessPoints} />
          ) : null}
        </>
      ) : null}
    </>
  );
};
