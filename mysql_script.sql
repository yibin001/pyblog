-- phpMyAdmin SQL Dump
-- version 3.3.8.1
-- http://www.phpmyadmin.net
--
-- 主机: w.rdc.sae.sina.com.cn:3307
-- 生成日期: 2013 年 07 月 02 日 13:48
-- 服务器版本: 5.5.23
-- PHP 版本: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- 数据库: `app_yibinim`
--

-- --------------------------------------------------------

--
-- 表的结构 `py_category`
--

DROP TABLE IF EXISTS `py_category`;
CREATE TABLE IF NOT EXISTS `py_category` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `category` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `postcount` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=10 ;

-- --------------------------------------------------------

--
-- 表的结构 `py_comment`
--

DROP TABLE IF EXISTS `py_comment`;
CREATE TABLE IF NOT EXISTS `py_comment` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `postid` int(10) unsigned NOT NULL,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `created` int(10) unsigned NOT NULL,
  `status` tinyint(1) NOT NULL COMMENT '0-正常，1-已删除',
  `content` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `parentid` int(10) unsigned NOT NULL,
  `ip` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `isspam` tinyint(1) unsigned NOT NULL DEFAULT '0',
  `location` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=27 ;

-- --------------------------------------------------------

--
-- 表的结构 `py_config`
--

DROP TABLE IF EXISTS `py_config`;
CREATE TABLE IF NOT EXISTS `py_config` (
  `config_key` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `config_value` varchar(512) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`config_key`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 表的结构 `py_posts`
--

DROP TABLE IF EXISTS `py_posts`;
CREATE TABLE IF NOT EXISTS `py_posts` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `authorid` int(10) unsigned NOT NULL,
  `content` text COLLATE utf8_unicode_ci NOT NULL,
  `status` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '0-正常发布，1-草稿，2-已删除',
  `password` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `created` int(10) unsigned NOT NULL,
  `viewcount` int(10) unsigned NOT NULL,
  `commentcount` int(10) unsigned NOT NULL,
  `commentstatus` tinyint(1) unsigned NOT NULL COMMENT '0-启用评论，1-禁用评论',
  `lastmodifyed` int(10) unsigned NOT NULL,
  `alias` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `posttype` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '0-一般日志，1-独立页面',
  PRIMARY KEY (`id`),
  KEY `alias` (`alias`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=24 ;

-- --------------------------------------------------------

--
-- 表的结构 `py_post_category`
--

DROP TABLE IF EXISTS `py_post_category`;
CREATE TABLE IF NOT EXISTS `py_post_category` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `postid` int(10) unsigned NOT NULL,
  `categoryid` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=97 ;

-- --------------------------------------------------------

--
-- 表的结构 `py_post_tag`
--

DROP TABLE IF EXISTS `py_post_tag`;
CREATE TABLE IF NOT EXISTS `py_post_tag` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `postid` int(10) unsigned NOT NULL,
  `tagid` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=159 ;

-- --------------------------------------------------------

--
-- 表的结构 `py_tags`
--

DROP TABLE IF EXISTS `py_tags`;
CREATE TABLE IF NOT EXISTS `py_tags` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `tag` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `postcount` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=12 ;

-- --------------------------------------------------------

--
-- 表的结构 `py_user`
--

DROP TABLE IF EXISTS `py_user`;
CREATE TABLE IF NOT EXISTS `py_user` (
  `userid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`userid`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=12 ;
