--
-- Base de datos: `hospital`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ecgs`
--

DROP TABLE IF EXISTS `ecgs`;
CREATE TABLE IF NOT EXISTS `ecgs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dni` varchar(10) NOT NULL,
  `alarma` float NOT NULL,
  `alarma_man` float NOT NULL,
  `qtc` float NOT NULL,
  `qtc_man` float NOT NULL,
  `qtc_type` int(1) NOT NULL,
  `incremento` float NOT NULL,
  `incremento_man` float NOT NULL,
  `contexto` float NOT NULL,
  `fecnac` varchar(10) NOT NULL,
  `sexo` varchar(6) NOT NULL,
  `diuretico` tinyint(1) NOT NULL,
  `suero` tinyint(1) NOT NULL,
  `sepsis` tinyint(1) NOT NULL,
  `medQT` tinyint(4) NOT NULL,
  `medsQT` tinyint(4) NOT NULL,
  `fullimage` longblob NOT NULL,
  `fullimageclipping` varchar(50) NOT NULL,
  `image` longblob NOT NULL,
  `time` varchar(20) NOT NULL,
  `m1` tinyint(1) NOT NULL,
  `m2` tinyint(1) NOT NULL,
  `m3` tinyint(1) NOT NULL,
  `m4` tinyint(1) NOT NULL,
  `m5` tinyint(1) NOT NULL,
  `observaciones` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=813 DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pacientes`
--

DROP TABLE IF EXISTS `pacientes`;
CREATE TABLE IF NOT EXISTS `pacientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `apellidos` varchar(50) NOT NULL,
  `dni` varchar(30) NOT NULL,
  `fecnac` varchar(10) NOT NULL,
  `sexo` varchar(6) NOT NULL,
  `iam` tinyint(1) NOT NULL,
  `cardiaco` tinyint(1) NOT NULL,
  `observaciones` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=44 DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `pacientes`
--

INSERT INTO `pacientes` (`id`, `nombre`, `apellidos`, `dni`, `fecnac`, `sexo`, `iam`, `cardiaco`, `observaciones`) VALUES
(42, 'Nombre-0001', 'Apellidos-0001', '0001', '1945-01-01', '1', 0, 0, '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int(11) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `username`, `password`) VALUES
(1, 'sani', 'faa2020');

