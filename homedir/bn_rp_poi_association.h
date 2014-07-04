/***************************************************************************
 * 
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/

/**
 * @file bn_rp_poi_association.h
 * @author dengweiru(dengweiru@baidu.com)
 * @date 2014-6-26 上午2:27:37
 * @code gbk
 * @brief 
 *  
 **/

#ifndef BN_RP_UPP_H_
#define BN_RP_UPP_H_

#include <string>
//using std::string;
#include <vector>
using namespace std;

//#include "bn_rp_svr_const_data.h"
//#include "bn_rp_svr_log.h"
//#include "bn_rp_svr_conf.h"

#include "google/protobuf/text_format.h"

#include "google/protobuf/stubs/common.h"
#include "sofa/pbrpc/rpc_channel.h"
#include "sofa/pbrpc/common.h"
#include "sofa/pbrpc/rpc_controller.h"

#include <sofa/pbrpc/pbrpc.h>
#include "pbrpc.pb.h"
#include "pbrpc_service.pb.h"

namespace bn_rp_svr
{

class AssociatPoiNode
{
public:
    uint64_t m_poi;     // poi id
    float m_score;      // 得分，分值越大相关性越高
    float m_x;          // 摩卡托坐标 x
    float m_y;          // 摩卡托坐标y
    string m_poi_name;  // poi的名称
public:
    AssociatPoiNode();
    virtual ~AssociatPoiNode();

    /**
     * 测试用，打印出信息
     */
    string DebugString();
};

class BNRPAssociator
{
public:
    vector<AssociatPoiNode> m_associat_poi_list; // soul服务返回的结果存在这里
public:
    BNRPAssociator();
    virtual ~BNRPAssociator();
public:
    /**
     * req_source 0为app 1为pc
     */
    bool GetPoiRecomList(string str_ip_port,string algorithm_id,const int req_source,double x, double y, int area_id, vector<uint64_t> poi_list);

protected:
    bool ConstructSoulRequest(lbs::da::openservice::GetBNItemsRequest &request,const int req_source,double x, double y, int area_id, vector<uint64_t> poi_list, 
        const char *soul_default_algorithm_id);

    bool ParseSoulResponse(lbs::da::openservice::GetBNItemsResponse &response);
};

} /* namespace upps */
#endif /* BN_RP_UPP_H_ */
