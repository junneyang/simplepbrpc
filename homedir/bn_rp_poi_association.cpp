/***************************************************************************
 * 
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 * 
 **************************************************************************/

/**
 * @file bn_rp_poi_association.cpp
 * @author dengweiru(dengweiru@baidu.com)
 * @date 2014-6-26 上午2:27:37
 * @code gbk
 * @brief 
 *  
 **/
#include "bn_rp_poi_association.h"
#include <sstream>
#include <iostream>
using namespace std;


using lbs::da::openservice::GetBNItemsRequest;
using lbs::da::openservice::GetBNItemsResponse;
using lbs::da::openservice::ItemBytes;


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <iconv.h>

#ifndef ICONV_CONST
# define ICONV_CONST const
#endif


namespace bn_rp_svr
{

AssociatPoiNode::AssociatPoiNode():
        m_poi(0),
        m_score(0),
        m_x(0),
        m_y(0),
        m_poi_name()
{
    // nothing
}

AssociatPoiNode::~AssociatPoiNode()
{
    // nothing
}

string AssociatPoiNode::DebugString()
{
    std::stringstream ss;
    /*ss << "poi:[" << m_poi
            << "] m_score:[" << m_score
            << "] m_x:[" << m_x
            << "] m_y:[" << m_y
            << "] m_poi_name:[" << m_poi_name << "]";*/
	ss << "[" << m_poi
            << "," << m_score
            << "," << m_x
            << "," << m_y
            << "," << m_poi_name << "]";
    return ss.str();
}

BNRPAssociator::BNRPAssociator():
        m_associat_poi_list()
{
    // TODO Auto-generated constructor stub
}

BNRPAssociator::~BNRPAssociator()
{
    // TODO Auto-generated destructor stub
}

bool BNRPAssociator::GetPoiRecomList(string str_ip_port,string algorithm_id,const int req_source,double x, double y, int area_id, vector<uint64_t> poi_list)
    {
        // 全局变量，需要传过来
        const uint32_t &soul_time_out = 3000;
        const char *soul_ip_port = str_ip_port.c_str(); //"10.48.55.39:7789";
        const char *soul_default_algorithm_id = algorithm_id.c_str(); //"bnitems";
        //
        sofa::pbrpc::RpcClientOptions client_options;
        sofa::pbrpc::RpcClient rpc_client(client_options);
        // Define an rpc channel.
        sofa::pbrpc::RpcChannelOptions channel_options;
        sofa::pbrpc::RpcChannel rpc_channel(&rpc_client, soul_ip_port, channel_options);

        // Prepare parameters.
        sofa::pbrpc::RpcController cntl;
        cntl.SetTimeout(soul_time_out);

        GetBNItemsRequest request;
        ConstructSoulRequest(request,req_source,x,y,area_id,poi_list,soul_default_algorithm_id);

        GetBNItemsResponse response;

        // Sync call.
        lbs::da::openservice::ItemService_Stub stub(&rpc_channel);
        stub.GetBNItemsByItem(&cntl, &request, &response, NULL);

        // Check if the request has been sent.
        // If has been sent, then can get the sent bytes.
//        MERGER_LOG_DEBUG("RemoteAddress=%s", cntl.RemoteAddress().c_str());
//        MERGER_LOG_DEBUG("IsRequestSent=%s", cntl.IsRequestSent() ? "true" : "false");
/*        if (cntl.IsRequestSent())
        {
            MERGER_LOG_DEBUG("LocalAddress=%s", cntl.LocalAddress().c_str());
            MERGER_LOG_DEBUG("SentBytes=%ld", cntl.SentBytes());
        }*/

        // Check if failed.
        if (cntl.Failed())
        {

            printf("request failed: %s", cntl.ErrorText().c_str());
            return false;
        }
        else
        {
			//#ifdef POI_DEBUG
			// for debug

			/*cout << "request [" << request.query() << "] ";
			for (int i = 0; i < request.item_ids_size(); ++i)
			{
				cout << "[" << *reinterpret_cast<const uint64_t*>(request.item_ids(i).c_str()) << "] ";
			}
			cout << " x:" << request.x() << " y:" << request.y() << endl;*/

			//#endif
            // 解析结果
            return ParseSoulResponse(response);
        }
    }

bool BNRPAssociator::ConstructSoulRequest(lbs::da::openservice::GetBNItemsRequest &request,const int req_source,double x, double y, int area_id, vector<uint64_t> poi_list, 
        const char *soul_default_algorithm_id)
{
    // 填充请求包
    lbs::da::openservice::RequestHeader* header = request.mutable_header();
    header->set_servicekey("key1"); // 头部固定的字符串，laplace暂时没检查
    header->set_secretkey("pass");
    header->set_subservice("sub");

    request.set_algorithmid(soul_default_algorithm_id);
    request.set_limit(1000); // soul暂时对本参数不起作用
    request.set_source(req_source); // 0为app 1为pc
	
	request.set_userid("xuxingjun");
	request.set_cuid("hitskyer");
	request.set_baidu_id("");
	request.set_nm_key("");
	request.set_coor_sys("baidu");
	request.set_x(x);
	request.set_y(y);
	request.set_area_id(area_id);

	vector<uint64_t> item_ids;
	for (std::vector<uint64_t>::const_iterator itr = poi_list.begin();
            itr != poi_list.end(); ++itr)
    {
		item_ids.push_back(*itr);
    }
	
    request.set_item_id_format(1); // 0为string可视格式，1为uint64_t格式
    for (std::vector<uint64_t>::const_iterator itr = item_ids.begin();
            itr != item_ids.end(); ++itr)
    {
        request.add_item_ids((&(*itr)), sizeof(uint64_t));
    }
	
    return true;
}

bool BNRPAssociator::ParseSoulResponse(lbs::da::openservice::GetBNItemsResponse &response)
{
	//#ifdef POI_DEBUG
	//cout << "response size [" << response.items_size() << "]" << endl;
	//#endif
    // soul保证返回的结果是有序的，从可信到不可信
    for(int i = 0; i < response.items_size(); ++i)
    {
        const ItemBytes &item = response.items(i);
        m_associat_poi_list.push_back(AssociatPoiNode());
        AssociatPoiNode &this_node = m_associat_poi_list.back();

        this_node.m_poi = strtoull(item.id().c_str(), NULL, 10);
        uint32_t f_value_size = item.value_size();
        this_node.m_score = f_value_size > 0 ? item.value(0) : 0;
        this_node.m_x = f_value_size > 2 ? item.value(2) : 0;
        this_node.m_y = f_value_size > 3 ? item.value(3) : 0;

        this_node.m_poi_name = item.str_value_size() > 0 ? item.str_value(0) : "";
		//cout<<this_node.m_poi_name<<endl;
		//#ifdef POI_DEBUG
		cout << this_node.DebugString() << endl;
		//#endif
	}
	return true;
}

} /* namespace upps */



int main(int argc, char** argv){
	using namespace bn_rp_svr;
	using namespace std;
	BNRPAssociator *bn=new BNRPAssociator();

	string str_ip_port(argv[1]);
	string algorithm_id(argv[2]);
	
	const int req_source=atoi(argv[3]);
	double x=atof(argv[4]);
	double y=atof(argv[5]);
	int area_id=atoi(argv[6]);
	vector<uint64_t> poi_list;
	for(int i=7; i<=argc-1; i++){
		poi_list.push_back(strtoul(argv[i],NULL, 10));
	}
	
	bn->GetPoiRecomList(str_ip_port,algorithm_id,req_source,x,y,area_id,poi_list);

	
	delete bn;
	return 0;
}

